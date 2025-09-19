import os
import sys
from typing import Any, Dict, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import asyncio
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Import the create_working_agent function instead of the class directly
from src.app.agent.working_agent import create_working_agent
from src.app.config.settings import settings

# Local imports
from src.app.services.transcription_service import TranscriptionService

# Singleton for File default
_FILE_DEFAULT = File(...)

app = FastAPI(title=settings.api.TITLE, version=settings.api.VERSION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.CORS_ORIGINS,
    allow_credentials=settings.api.CORS_CREDENTIALS,
    allow_methods=settings.api.CORS_METHODS,
    allow_headers=settings.api.CORS_HEADERS,
)

# Initialize the transcription service
transcription_service = TranscriptionService()


# Application state for working agent
class AppState:
    """Application state container."""

    def __init__(self) -> None:
        self.working_agent: Optional[Any] = None


app_state = AppState()


async def initialize_agent() -> None:
    """Initialize the working agent"""
    if app_state.working_agent is None:
        print("Initializing WorkingAgent...")
        app_state.working_agent = await create_working_agent()
        print("WorkingAgent initialized successfully")


@app.on_event("startup")
async def startup_event() -> None:
    print("Application startup complete")
    # Initialize the working agent
    await initialize_agent()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    print("Application shutdown initiated")

    # Clean up working agent resources
    if app_state.working_agent is not None:
        try:
            print("Cleaning up WorkingAgent...")
            app_state.working_agent.cleanup()
        except Exception as e:
            print(f"Error cleaning up WorkingAgent: {e}")

    # Clean up transcription service
    try:
        print("Cleaning up TranscriptionService...")
        TranscriptionService.shutdown()
    except Exception as e:
        print(f"Error cleaning up TranscriptionService: {e}")

    print("Application shutdown completed")


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Speech Transcription API is running"}


@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = _FILE_DEFAULT) -> Dict[str, str]:
    try:
        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(
            suffix=settings.audio.TEMP_AUDIO_SUFFIX, delete=False
        ) as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            temp_filename = tmp_file.name

        try:
            # Transcribe the audio file with timeout
            transcription = await asyncio.wait_for(
                transcription_service.transcribe_file(temp_filename),
                timeout=settings.api.TRANSCRIPTION_TIMEOUT,
            )

            # Remove the temporary file
            os.unlink(temp_filename)

            if transcription is not None:
                return {"transcription": transcription}
            else:
                raise HTTPException(status_code=500, detail="Transcription failed")

        except asyncio.TimeoutError as e:
            # Remove the temporary file if an error occurred
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise HTTPException(
                status_code=500,
                detail="Transcription timeout - audio processing took too long",
            ) from e
        except Exception as e:
            # Remove the temporary file if an error occurred
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise HTTPException(
                status_code=500, detail=f"Transcription error: {e!s}"
            ) from e

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Request processing error: {e!s}"
        ) from e


@app.post("/transcribe_and_act")
async def transcribe_and_act(audio: UploadFile = _FILE_DEFAULT) -> Dict[str, str]:
    try:
        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(
            suffix=settings.audio.TEMP_AUDIO_SUFFIX, delete=False
        ) as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            temp_filename = tmp_file.name

        try:
            # Make sure agent is initialized
            await initialize_agent()

            # Transcribe the audio file with timeout
            transcription = await asyncio.wait_for(
                transcription_service.transcribe_file(temp_filename),
                timeout=settings.api.TRANSCRIPTION_TIMEOUT,
            )

            print(f"Transcription completed: {transcription}")

            if transcription is not None:
                # Remove the temporary file
                os.unlink(temp_filename)

                # Process with working agent
                return await _process_with_agent(transcription)
            else:
                # Remove the temporary file if an error occurred
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                raise HTTPException(status_code=500, detail="Transcription failed")

        except asyncio.TimeoutError as e:
            # Remove the temporary file if an error occurred
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise HTTPException(
                status_code=500,
                detail="Transcription timeout - audio processing took too long",
            ) from e
        except Exception as e:
            # Remove the temporary file if an error occurred
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            print(f"Transcription error: {e!s}")
            raise HTTPException(
                status_code=500, detail=f"Transcription error: {e!s}"
            ) from e

    except HTTPException:
        raise
    except Exception as e:
        print(f"Request processing error: {e!s}")
        raise HTTPException(
            status_code=500, detail=f"Request processing error: {e!s}"
        ) from e


async def _process_with_agent(transcription: str) -> Dict[str, str]:
    """Process transcription with working agent."""
    if app_state.working_agent is None:
        print("Agent not initialized")
        return {
            "transcription": transcription,
            "action_result": "Agent not initialized",
        }

    print(f"Processing command with WorkingAgent: {transcription}")
    response_messages = []
    async for message in app_state.working_agent.full_round(transcription):
        response_messages.append(message)
        print(f"Message received: Role={message.role}, Content={message.content}")
        # Debug: Check for tool calls
        if hasattr(message, "tool_calls") and message.tool_calls:
            print(f"Tool calls found: {message.tool_calls}")

    # Extract the final response from the agent
    assistant_response = ""
    function_response = ""
    tool_calls_found = False

    for msg in response_messages:
        if str(msg.role) == "ChatRole.ASSISTANT" and msg.content:
            assistant_response = msg.content
        elif str(msg.role) == "ChatRole.FUNCTION" and msg.content:
            function_response = msg.content
        # Check for tool calls in any message
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            tool_calls_found = True
            print(f"Tool calls detected in message: {msg.tool_calls}")

    result = function_response if function_response else assistant_response
    print(f"Action result: {result}")
    print(f"Tool calls found during processing: {tool_calls_found}")

    return {"transcription": transcription, "action_result": result}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api.HOST, port=settings.api.PORT)
