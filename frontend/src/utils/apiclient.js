export const send_auth = async (initdata) => {
  let resp = await fetch(`${import.meta.env.VITE_API_URL}/telegram/auth/webapp`, {
    method: 'POST',
    body: JSON.stringify({ initData: initdata }),
  })
  console.log(resp)
}