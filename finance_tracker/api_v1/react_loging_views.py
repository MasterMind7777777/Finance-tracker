from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import logging

# Initialize logger
logger = logging.getLogger("react_loging_views")


@api_view(["POST"])
def react_logging_view(request):
    if request.method == "POST":
        try:
            if "level" not in request.data or "message" not in request.data:
                return Response(
                    {"status": "error", "error": "Insufficient data"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            level = request.data["level"]
            message = request.data["message"]
            module = request.data.get("module", "UnknownModule")
            extra = request.data.get("extra", {})

            # Add username to extra
            user = (
                request.user.username
                if request.user.is_authenticated
                else "Anonymous"
            )
            extra["user"] = user

            log_method = getattr(logger, level.lower(), None)
            if log_method is None:
                return Response(
                    {"status": "error", "error": "Invalid log level"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            extra["frontend_module"] = module
            log_method(message, extra=extra)

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Failed to log message", extra={"exception": str(e)})
            return Response(
                {"status": "error", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
