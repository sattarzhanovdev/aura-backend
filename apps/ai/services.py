import json
import os
from typing import Any

import httpx
from django.db import transaction

from .models import AiGenerationGroup, AiGenerationTask

KIE_MARKET_BASE_URL = "https://api.kie.ai"
KIE_FILE_BASE_URL = "https://kieai.redpandaai.co"
KIE_NANO_MODEL = "nano-banana-2"
KIE_GEMINI_MODEL = "gemini-3-flash"


class KieConfigurationError(RuntimeError):
    pass


def _get_kie_headers() -> dict[str, str]:
    token = os.environ.get("KIE_API_KEY")
    if not token:
        raise KieConfigurationError("KIE_API_KEY environment variable is not set.")
    return {"Authorization": f"Bearer {token}"}


def _get_callback_url() -> str | None:
    base_url = os.environ.get("AURA_PUBLIC_BASE_URL", "").rstrip("/")
    if not base_url:
        return None
    return f"{base_url}/api/style/kie/callback"


def _client() -> httpx.Client:
    return httpx.Client(timeout=60.0)


def upload_base64_image(*, base64_data: str, file_name: str) -> str:
    with _client() as client:
        response = client.post(
            f"{KIE_FILE_BASE_URL}/api/file-base64-upload",
            headers={**_get_kie_headers(), "Content-Type": "application/json"},
            json={
                "base64Data": base64_data,
                "uploadPath": "images/aura",
                "fileName": file_name,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return payload["data"]["downloadUrl"]


def _extract_json_block(raw_text: str) -> dict[str, Any]:
    cleaned = raw_text.strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        cleaned = next((part for part in parts if "{" in part and "}" in part), cleaned)
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model response.")
    return json.loads(cleaned[start : end + 1])


def analyze_clothing_from_image(*, base64_data: str) -> dict[str, Any]:
    image_url = upload_base64_image(
        base64_data=base64_data,
        file_name="clothing-analysis.png",
    )
    prompt = (
        "You are analyzing a single clothing item photo for a fashion app. "
        "Return strict JSON only with keys: name, description, color, category, style_tags. "
        "Use concise product-style naming. "
        "Category must be one of: top, bottom, shoes, accessory, outerwear, dress. "
        "style_tags must be an array of 2 to 4 short strings."
    )
    with _client() as client:
        response = client.post(
            f"{KIE_MARKET_BASE_URL}/{KIE_GEMINI_MODEL}/v1/chat/completions",
            headers={**_get_kie_headers(), "Content-Type": "application/json"},
            json={
                "model": KIE_GEMINI_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                "stream": False,
            },
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        result = _extract_json_block(content)
        result["image_url"] = image_url
        return result


def build_outfit_prompt(*, wardrobe_items: list[dict[str, Any]], weather: str, occasion: str) -> str:
    lines = []
    for item in wardrobe_items[:12]:
        lines.append(
            f"{item.get('name', 'item')} | category={item.get('category', '')} | "
            f"color={item.get('color', '')} | style={item.get('style', '')} | "
            f"description={item.get('description', '')} | "
            f"patterns={', '.join(item.get('styleTags', []) if isinstance(item.get('styleTags'), list) else [])}"
        )
    wardrobe_summary = "; ".join(lines) if lines else "no wardrobe references provided"
    return (
        "Create a premium editorial outfit visualization for a mobile fashion app. "
        f"Occasion: {occasion}. Weather: {weather}. "
        f"Use these wardrobe references: {wardrobe_summary}. "
        "The output must be vertical only, in a portrait 9:16 composition. "
        "Always frame it as a tall editorial mobile-first fashion image, never landscape or square. "
        "Keep the subject arranged for a vertical full-body composition. "
        "Treat every uploaded clothing image as a strict source garment reference. "
        "Do not redesign, simplify, clean up, or replace the clothing details. "
        "Preserve the original garment identity exactly: same print placement, same pattern, same graphics, "
        "same logos, same embroidery, same stripes, same texture, same fabric blocks, same color distribution, "
        "same visible details and trims. "
        "If a shirt has a pattern or text, keep that pattern or text visually consistent instead of inventing a new one. "
        "Do not turn patterned clothes into plain clothes. Do not remove decorative details. "
        "Build the look around the real garment references exactly as provided. "
        "The image should look like a stylish full-body fashion photo with believable styling, "
        "cohesive colors, clean silhouette, soft luxury lighting, premium texture detail, "
        "and realistic clothing composition. Avoid text overlays and collages."
    )


def create_outfit_generation_group(
    *,
    wardrobe_items: list[dict[str, Any]],
    image_base64_list: list[str],
    weather: str,
    occasion: str,
    variant_count: int = 3,
) -> AiGenerationGroup:
    uploaded_images = [
        upload_base64_image(base64_data=image_data, file_name=f"outfit-ref-{index + 1}.png")
        for index, image_data in enumerate(image_base64_list[:4])
    ]
    prompt = build_outfit_prompt(
        wardrobe_items=wardrobe_items,
        weather=weather,
        occasion=occasion,
    )
    callback_url = _get_callback_url()

    with transaction.atomic():
        group = AiGenerationGroup.objects.create(
            request_type="outfit_generation",
            prompt=prompt,
            weather_summary=weather,
            occasion=occasion,
            metadata={"reference_images": uploaded_images},
        )

        for index in range(variant_count):
            variant_prompt = (
                f"{prompt} Variation {index + 1}. "
                "Keep the same wardrobe logic and preserve the same exact garment details, "
                "but vary pose, framing, and styling nuance only."
            )
            payload = {
                "model": KIE_NANO_MODEL,
                "input": {
                    "prompt": variant_prompt,
                    "image_input": uploaded_images,
                    "aspect_ratio": "9:16",
                    "resolution": "1K",
                    "output_format": "png",
                },
            }
            if callback_url:
                payload["callBackUrl"] = callback_url

            with _client() as client:
                response = client.post(
                    f"{KIE_MARKET_BASE_URL}/api/v1/jobs/createTask",
                    headers={**_get_kie_headers(), "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                task_payload = response.json()
                provider_task_id = task_payload["data"]["taskId"]

            AiGenerationTask.objects.create(
                group=group,
                variant_index=index + 1,
                provider_model=KIE_NANO_MODEL,
                provider_task_id=provider_task_id,
                prompt=variant_prompt,
                input_image_urls=uploaded_images,
            )

    return refresh_generation_group(group.id)


def _parse_result_urls(result_json: str | dict[str, Any] | None, callback_payload: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    if isinstance(result_json, str) and result_json:
        try:
            parsed = json.loads(result_json)
        except json.JSONDecodeError:
            parsed = {}
    elif isinstance(result_json, dict):
        parsed = result_json
    else:
        parsed = {}

    urls.extend(parsed.get("resultUrls", []))
    urls.extend(parsed.get("result_urls", []))

    info = callback_payload.get("data", {}).get("info", {})
    result_image_url = info.get("resultImageUrl")
    if result_image_url:
        urls.append(result_image_url)
    result_urls = info.get("resultUrls") or info.get("result_urls") or []
    if isinstance(result_urls, list):
        urls.extend(result_urls)

    deduped = []
    for url in urls:
        if url and url not in deduped:
            deduped.append(url)
    return deduped


def refresh_task_from_provider(task: AiGenerationTask) -> AiGenerationTask:
    with _client() as client:
        response = client.get(
            f"{KIE_MARKET_BASE_URL}/api/v1/jobs/recordInfo",
            headers=_get_kie_headers(),
            params={"taskId": task.provider_task_id},
        )
        response.raise_for_status()
        payload = response.json()["data"]

    task.state = payload.get("state", task.state)
    task.progress = payload.get("progress", task.progress) or 0
    task.fail_code = payload.get("failCode", "") or ""
    task.error_message = payload.get("failMsg", "") or ""
    task.result_urls = _parse_result_urls(payload.get("resultJson"), task.callback_payload)
    task.save(
        update_fields=[
            "state",
            "progress",
            "fail_code",
            "error_message",
            "result_urls",
            "updated_at",
        ]
    )
    return task


def _sync_group_state(group: AiGenerationGroup) -> AiGenerationGroup:
    tasks = list(group.tasks.all())
    if tasks and all(task.state == "success" for task in tasks):
        group.state = "success"
    elif any(task.state == "fail" for task in tasks):
        group.state = "fail"
    elif any(task.state in {"generating", "queuing"} for task in tasks):
        group.state = "processing"
    else:
        group.state = "queued"
    group.save(update_fields=["state", "updated_at"])
    return group


def refresh_generation_group(group_id) -> AiGenerationGroup:
    group = AiGenerationGroup.objects.prefetch_related("tasks").get(id=group_id)
    for task in group.tasks.all():
        if task.state not in {"success", "fail"} or not task.result_urls:
            refresh_task_from_provider(task)
    return _sync_group_state(AiGenerationGroup.objects.prefetch_related("tasks").get(id=group_id))


def handle_kie_callback(payload: dict[str, Any]) -> None:
    provider_task_id = (
        payload.get("data", {}).get("taskId")
        or payload.get("data", {}).get("task_id")
        or payload.get("taskId")
        or payload.get("task_id")
    )
    if not provider_task_id:
        return
    try:
        task = AiGenerationTask.objects.select_related("group").get(provider_task_id=provider_task_id)
    except AiGenerationTask.DoesNotExist:
        return

    task.callback_payload = payload
    callback_code = payload.get("code")
    callback_msg = payload.get("msg", "") or ""
    callback_urls = _parse_result_urls(None, payload)

    if callback_code == 200:
        task.state = "success"
        task.progress = 100
        task.result_urls = callback_urls
        task.error_message = ""
        task.fail_code = ""
    elif callback_code in {400, 500, 501}:
        task.state = "fail"
        task.error_message = callback_msg
        task.fail_code = str(callback_code)

    task.save(
        update_fields=[
            "callback_payload",
            "state",
            "progress",
            "result_urls",
            "error_message",
            "fail_code",
            "updated_at",
        ]
    )

    if task.state not in {"success", "fail"} or not task.result_urls:
        refresh_task_from_provider(task)
    _sync_group_state(task.group)


def serialize_group(group: AiGenerationGroup) -> dict[str, Any]:
    return {
        "id": str(group.id),
        "state": group.state,
        "request_type": group.request_type,
        "prompt": group.prompt,
        "weather_summary": group.weather_summary,
        "occasion": group.occasion,
        "reference_images": group.metadata.get("reference_images", []),
        "variants": [
            {
                "id": str(task.id),
                "variant_index": task.variant_index,
                "provider_task_id": task.provider_task_id,
                "state": task.state,
                "progress": task.progress,
                "result_urls": task.result_urls,
                "error_message": task.error_message,
            }
            for task in group.tasks.all().order_by("variant_index")
        ],
    }
