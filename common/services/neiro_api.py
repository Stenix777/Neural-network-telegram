import json
from enum import Enum
from json import JSONDecodeError
from typing import Literal

from aiohttp import ClientSession
from loguru import logger
from pydantic import BaseModel

from common.enums import (ImageAction, ImageModels, ServiceModels, TextModels,
                          VideoModels)


class GenerationStatus(str, Enum):
    WAITING = "waiting"
    IN_QUEUE = "in_queue"
    IN_PROCESS = "in_process"
    READY = "ready"
    BANNED = "banned"
    ERROR = "error"


class ResponseResult(BaseModel):
    success: bool = True
    status: GenerationStatus | None = None
    result: str | list | None = ""


class AsyncNeiroAPI:
    def __init__(self, token):
        self.headers = {"x-api-key": token}
        self.base_url = "https://api.xn--e1aajcsinjk.com/v1"
        self.completion_urls = {
            TextModels.GPT_3_TURBO: f"{self.base_url}/openai/completion/",
            TextModels.GPT_4_TURBO: f"{self.base_url}/openai/completion/",
            TextModels.YAGPT: f"{self.base_url}/yandex/completion/",
            TextModels.YAGPT_LITE: f"{self.base_url}/yandex/completion/",
            TextModels.CLAUDE: f"{self.base_url}/claude/completion/",
            TextModels.GEMINI: f"{self.base_url}/gemini/completion/",
        }
        self.imagine_urls = {
            ImageModels.MIDJOURNEY: f"{self.base_url}/midjourney/imagine/",
            ImageModels.KANDINSKY: f"{self.base_url}/kandinsky/generate/",
            ImageModels.STABLE_DIFFUSION: f"{self.base_url}/stablediffusion/text2img/",
        }
        self.status_urls = {
            ImageModels.MIDJOURNEY: f"{self.base_url}/midjourney/check-task/",
            ImageModels.KANDINSKY: f"{self.base_url}/kandinsky/check-task/",
            ImageModels.STABLE_DIFFUSION: f"{self.base_url}/stablediffusion/check-task/",
        }
        self.status_urls.update({model: f"{self.base_url}/services/check-task/" for model in ServiceModels})

    async def imagine(self, model: ImageModels, prompt: str) -> ResponseResult:
        url = self.imagine_urls[model]
        payload = {"prompt": prompt}

        result = await self.__request(url=url, payload=payload)

        if not result:
            return ResponseResult(success=False)
        return ResponseResult(result=result["task_id"])

    async def midjourney_action(self, action: ImageAction, index: int, task_id: str) -> ResponseResult:
        url = f"{self.base_url}/midjourney/action/"
        payload = {"action": action.value, "index": index, "task_id": task_id}

        result = await self.__request(url=url, payload=payload)

        if not result:
            return ResponseResult(success=False)
        return ResponseResult(result=result["task_id"])

    async def dalle_imagine(self, model: ImageModels, prompt: str) -> ResponseResult:
        url = f"{self.base_url}/openai/image/"
        payload = {"model": model, "prompt": prompt}

        result = await self.__request(url=url, payload=payload)

        if not result.get("result"):
            if result.get("detail") == "content_policy_violation":
                return ResponseResult(success=False, status=GenerationStatus.BANNED)
            return ResponseResult(success=False, status=GenerationStatus.ERROR)
        return ResponseResult(result=result["result"][0])

    async def completion(self, model: TextModels,
                         conversation: list[dict[Literal["role", "content"], str]]) -> ResponseResult:
        url = self.completion_urls[model]
        payload = {"model": model, "messages": conversation}

        result = await self.__request(url=url, payload=payload)

        if not result.get("result"):
            return ResponseResult(success=False)
        return ResponseResult(result=result["result"])

    async def vision(self, img_url: str, prompt: str) -> ResponseResult:
        url = f"{self.base_url}/openai/vision/"
        payload = {"image_url": img_url, "text": prompt}

        result = await self.__request(url=url, payload=payload)

        if not result.get("result"):
            return ResponseResult(success=False)
        return ResponseResult(result=result["result"])

    async def video_generation(self, model: VideoModels, params: dict) -> ResponseResult:
        url = f"{self.base_url}/stablediffusion/{model.value}/"

        result = await self.__request(url=url, payload=params)

        if not result.get("task_id"):
            return ResponseResult(success=False)
        return ResponseResult(result=result["task_id"])

    async def service_generation(self, model: ServiceModels, params: dict) -> ResponseResult:
        url = f"{self.base_url}/services/{model.value}/"

        result = await self.__request(url=url, payload=params)

        if not result.get("task_id"):
            return ResponseResult(success=False)
        return ResponseResult(result=result["task_id"])

    async def get_status(self, task_id: str, model: ImageModels | VideoModels) -> ResponseResult:
        url = self.status_urls[model]
        payload = {"task_id": task_id}

        result = await self.__request(url=url, payload=payload)

        if not result:
            return ResponseResult(success=False)
        return ResponseResult(status=result["status"], result=result["result"])

    async def speech_to_text(self, voice_url: str) -> ResponseResult:
        url = f"{self.base_url}/services/speech-to-text/"
        payload = {"url_to_file": voice_url}

        result = await self.__request(url=url, payload=payload)

        if not result or result.get("status") != "ready":
            return ResponseResult(success=False)
        return ResponseResult(result=result["result"])

    async def translate(self, text: str, from_lang: str = "ru", to_lang: str = "en"):
        url = f"{self.base_url}/services/translate/"
        payload = {"text": text, "from_lang": from_lang, "to_lang": to_lang}

        result = await self.__request(url=url, payload=payload)

        if not result or result.get("status") != "ready":
            return ResponseResult(success=False)
        return ResponseResult(result=result["result"])

    async def __request(self, url: str, payload: dict) -> dict | None:
        async with ClientSession(headers=self.headers) as session:
            async with session.post(url=url, json=payload) as response:
                result = await response.text()
                try:
                    result = json.loads(result)
                except JSONDecodeError as error:
                    logger.error(f"API REQUEST JSON error: {error.args} | {result}")
                    return
                if not response.ok:
                    logger.error(f"API REQUEST error: {response.status} | {result}")
                return result
