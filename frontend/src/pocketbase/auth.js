import pb from './index';

export async function authWithTelegram(initData) {
  const res = await fetch(`${import.meta.env.VITE_POCKETBASE_URL}/api/auth/telegram`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ initData }),
  });
  const data = await res.json();
  if (res.ok) {
    pb.authStore.save(data.token, data.record);
    return data;
  } else {
    throw new Error(data.error || 'Auth failed');
  }
}

export default { authWithTelegram };
