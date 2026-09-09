
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
//Common API types
export interface ApiErrorResponse {
  detail?: string;
  message?: string;
}

export interface ApiMessageResponse {
  message: string;
}
//Register 
export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  terms_accepted: boolean;
}

export interface RegisterResponse {
  message: string;
  user: unknown;
}

//social auth
export interface SocialLoginRequest {
  provider: 'google' | 'github' | 'facebook';
}

export interface SocialLoginResponse {
  url: string;
}

//API client
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(
    `${API_URL}${endpoint}`,
    {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    }
  );

  const data = await response
    .json()
    .catch(() => null);

  if (!response.ok) {
    const errorMessage =
      data &&
      typeof data === 'object' &&
      'detail' in data &&
      typeof data.detail === 'string'
        ? data.detail
        : data &&
            typeof data === 'object' &&
            'message' in data &&
            typeof data.message === 'string'
          ? data.message
          : 'Something went wrong. Please try again.';

    throw new Error(errorMessage);
  }

  return data as T;
}

//Auth API
export const registerUser = (
  payload: RegisterRequest
) => {
  return apiRequest<RegisterResponse>(
    '/api/v1/auth/register',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    }
  );
};

export const startSocialLogin = (
  payload: SocialLoginRequest
) => {
  return apiRequest<SocialLoginResponse>(
    '/api/v1/auth/social',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    }
  );
};

//verify-email
export interface ResendVerificationRequest {
  email: string;
}

export const resendVerification = (
  payload: ResendVerificationRequest
) => {
  return apiRequest<ApiMessageResponse>(
    '/api/v1/auth/resend-verification',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    }
  );
};

//Login
export interface LoginRequest {
  email: string;
  password: string;
  remember_me: boolean;
}

export interface LoginResponse {
  message?: string;
  detail?: string;
  requires_mfa?: boolean;
  user_id?: string;
  session?: {
    access_token?: string;
    refresh_token?: string;
    expires_in?: number;
    token_type?: string;
  };
}

export const loginUser = (
  payload: LoginRequest
) => {
  return apiRequest<LoginResponse>(
    '/api/v1/auth/login',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    }
  );
};

//MFA setup and verify 
export interface MFAEnrollResponse {
  id?: string;
  factor_id?: string;

  totp?: {
    uri?: string;
    secret?: string;
    qr_code?: string;
  };

  detail?: string;
  message?: string;
}

export interface MFAVerifyEnrollRequest {
  factor_id: string;
  code: string;
}

export interface MFAVerifyEnrollResponse {
  message?: string;

  session?: {
    access_token?: string;
    refresh_token?: string;
    expires_in?: number;
    token_type?: string;
  };

  detail?: string;
}

export interface MFAVerifyRequest {
  user_id: string;
  totp_code: string;
}

export interface MFAVerifyResponse {
  session?: {
    access_token?: string;
    refresh_token?: string;
    expires_in?: number;
    token_type?: string;
  };

  detail?: string;
  message?: string;
}

export const enrollMFA = (
  accessToken: string
) => {
  return apiRequest<MFAEnrollResponse>(
    '/api/v1/auth/mfa/enroll',
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );
};

export const verifyMFAEnrollment = (
  accessToken: string,
  payload: MFAVerifyEnrollRequest
) => {
  return apiRequest<MFAVerifyEnrollResponse>(
    '/api/v1/auth/mfa/verify-enroll',
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(payload),
    }
  );
};

export const verifyMFA = (
  accessToken: string,
  payload: MFAVerifyRequest
) => {
  return apiRequest<MFAVerifyResponse>(
    '/api/v1/auth/mfa/verify',
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(payload),
    }
  );
};
//Forgot and reset password

export interface ForgotPasswordRequest {
  email: string;
}


export interface ResetPasswordStatusResponse {
  requires_mfa: boolean;
  user_id: string;
}

export interface ResetPasswordRequest {
  access_token: string;
  new_password: string;
  totp_code?: string;
}

export const forgotPassword = (
  payload: ForgotPasswordRequest
) => {
  return apiRequest<ApiMessageResponse>(
    '/api/v1/auth/forgot-password',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    }
  );
};

export const resetPassword = (
  payload: ResetPasswordRequest
) => {
  return apiRequest<ApiMessageResponse>(
    '/api/v1/auth/reset-password',
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${payload.access_token}`,
      },
      body: JSON.stringify({
        new_password: payload.new_password,
        ...(payload.totp_code
          ? { totp_code: payload.totp_code }
          : {}),
      }),
    }
  );
};

export const checkResetPasswordMFAStatus = (
  accessToken: string
) => {
  return apiRequest<ResetPasswordStatusResponse>(
    '/api/v1/auth/reset-password/status',
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );
};