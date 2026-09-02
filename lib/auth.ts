export interface Session {
  access_token?: string;
  refresh_token?: string;
  expires_in?: number;
  token_type?: string;
}

const SESSION_KEY = 'unios_session';
const MFA_USER_ID_KEY = 'mfa_user_id';
const MFA_ACCESS_TOKEN_KEY = 'mfa_access_token';
const MFA_REMEMBER_ME_KEY = 'mfa_remember_me';
const LAST_ACTIVITY_KEY = 'unios_last_activity';
// 15 minutes of inactivity
const INACTIVITY_TIMEOUT = 15 * 60 * 1000;

export const saveSession = (
  session: Session,
  rememberMe = false
) => {
  const storage = rememberMe ? localStorage : sessionStorage;

  storage.setItem(SESSION_KEY, JSON.stringify(session));

  // Prevent stale duplicate sessions in the other storage.
  const otherStorage = rememberMe ? sessionStorage : localStorage;
  otherStorage.removeItem(SESSION_KEY);

  // Start inactivity tracking from the moment the session is created.
  updateLastActivity();
};

export const getSession = (): Session | null => {
  const localSession = localStorage.getItem(SESSION_KEY);
  const sessionSession = sessionStorage.getItem(SESSION_KEY);

  const session = localSession || sessionSession;

  if (!session) {
    return null;
  }

  try {
    return JSON.parse(session) as Session;
  } catch {
    return null;
  }
};

export const getAccessToken = (): string | null => {
  const session = getSession();
  return session?.access_token || null;
};

export const getRememberMe = (): boolean => {
  return localStorage.getItem(SESSION_KEY) !== null;
};

//Inactivity session managment
export const updateLastActivity = () => {
  const session = getSession();

  if (!session?.access_token) {
    return;
  }

  localStorage.setItem(
    LAST_ACTIVITY_KEY,
    Date.now().toString()
  );
};

export const isSessionInactive = (): boolean => {
  const session = getSession();

  if (!session?.access_token) {
    return true;
  }

  const lastActivity = localStorage.getItem(LAST_ACTIVITY_KEY);

  if (!lastActivity) {
    // Existing session without an activity timestamp.
    // Treat the current moment as the starting point.
    updateLastActivity();
    return false;
  }

  const elapsed = Date.now() - Number(lastActivity);

  return elapsed >= INACTIVITY_TIMEOUT;
};

export const getInactivityTimeout = () => {
  return INACTIVITY_TIMEOUT;
};

//MFA session managment
export const setMfaRememberMe = (rememberMe: boolean) => {
  sessionStorage.setItem(
    MFA_REMEMBER_ME_KEY,
    String(rememberMe)
  );
};

export const getMfaRememberMe = (): boolean => {
  return (
    sessionStorage.getItem(MFA_REMEMBER_ME_KEY) === 'true'
  );
};

export const clearMfaSession = () => {
  sessionStorage.removeItem(MFA_USER_ID_KEY);
  sessionStorage.removeItem(MFA_ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(MFA_REMEMBER_ME_KEY);
};

//clear session
export const clearSession = () => {
  localStorage.removeItem(SESSION_KEY);
  sessionStorage.removeItem(SESSION_KEY);

  localStorage.removeItem(LAST_ACTIVITY_KEY);

  // Also clean temporary MFA credentials.
  clearMfaSession();
};