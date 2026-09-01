interface Session {
  access_token?: string;
  refresh_token?: string;
  expires_in?: number;
  token_type?: string;
}

const SESSION_KEY = 'unios_session';

export const saveSession = (
  session: Session,
  rememberMe = false
) => {
  const storage = rememberMe ? localStorage : sessionStorage;

  storage.setItem(SESSION_KEY, JSON.stringify(session));
};

export const getSession = (): Session | null => {
  const localSession = localStorage.getItem(SESSION_KEY);
  const sessionSession = sessionStorage.getItem(SESSION_KEY);

  const session = localSession || sessionSession;

  if (!session) {
    return null;
  }

  try {
    return JSON.parse(session);
  } catch {
    return null;
  }
};

export const clearSession = () => {
  localStorage.removeItem(SESSION_KEY);
  sessionStorage.removeItem(SESSION_KEY);
};

export const getAccessToken = (): string | null => {
  const session = getSession();

  return session?.access_token || null;
};