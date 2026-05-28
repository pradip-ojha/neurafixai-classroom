from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MessageData,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetRequestData,
    RefreshRequest,
    RegisterInstitutionData,
    RegisterInstitutionRequest,
    TokenPairResponse,
    VerifyEmailRequest,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register-institution", response_model=ApiResponse[RegisterInstitutionData], status_code=201)
async def register_institution(
    payload: RegisterInstitutionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RegisterInstitutionData]:
    data = await AuthService(db).register_institution(
        institution_name=payload.institution_name,
        institution_slug=payload.institution_slug,
        full_name=payload.full_name,
        email=str(payload.email),
        password=payload.password,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    return ApiResponse(
        data=RegisterInstitutionData(**data),
        message="Institution owner registered. Verify email before login.",
        request_id=request.state.request_id,
    )


@router.post("/verify-email", response_model=ApiResponse[MessageData])
async def verify_email(
    payload: VerifyEmailRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MessageData]:
    await AuthService(db).verify_email(token=payload.token)
    return ApiResponse(
        data=MessageData(message="Email verified."),
        message="Email verified.",
        request_id=request.state.request_id,
    )


@router.post("/login", response_model=ApiResponse[TokenPairResponse])
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenPairResponse]:
    token_pair = await AuthService(db).login(
        institution_slug=payload.institution_slug,
        email=str(payload.email),
        password=payload.password,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        device_name=payload.device_name,
    )
    return ApiResponse(
        data=TokenPairResponse(**token_pair.__dict__),
        message="Login successful.",
        request_id=request.state.request_id,
    )


@router.post("/refresh", response_model=ApiResponse[TokenPairResponse])
async def refresh(
    payload: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenPairResponse]:
    token_pair = await AuthService(db).refresh(
        refresh_token=payload.refresh_token,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    return ApiResponse(
        data=TokenPairResponse(**token_pair.__dict__),
        message="Token refreshed.",
        request_id=request.state.request_id,
    )


@router.post("/logout", response_model=ApiResponse[MessageData])
async def logout(
    payload: LogoutRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MessageData]:
    await AuthService(db).logout(refresh_token=payload.refresh_token)
    return ApiResponse(
        data=MessageData(message="Logged out."),
        message="Logged out.",
        request_id=request.state.request_id,
    )


@router.post("/logout-all", response_model=ApiResponse[MessageData])
async def logout_all(
    payload: LogoutRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MessageData]:
    await AuthService(db).logout_all(refresh_token=payload.refresh_token)
    return ApiResponse(
        data=MessageData(message="All sessions logged out."),
        message="All sessions logged out.",
        request_id=request.state.request_id,
    )


@router.post("/password-reset/request", response_model=ApiResponse[PasswordResetRequestData])
async def request_password_reset(
    payload: PasswordResetRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PasswordResetRequestData]:
    data = await AuthService(db).request_password_reset(
        institution_slug=payload.institution_slug,
        email=str(payload.email),
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    return ApiResponse(
        data=PasswordResetRequestData(**data),
        message="Password reset requested.",
        request_id=request.state.request_id,
    )


@router.post("/password-reset/confirm", response_model=ApiResponse[MessageData])
async def confirm_password_reset(
    payload: PasswordResetConfirmRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MessageData]:
    await AuthService(db).confirm_password_reset(
        token=payload.token,
        new_password=payload.new_password,
    )
    return ApiResponse(
        data=MessageData(message="Password reset complete."),
        message="Password reset complete.",
        request_id=request.state.request_id,
    )


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else None

