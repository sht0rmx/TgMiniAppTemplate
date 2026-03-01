import { ref } from 'vue'

const lifetime = 3000

export interface AlertItem {
  id: number
  type: string
  icon: string
  msg: string
  subKey: string
}

export const alerts = ref<AlertItem[]>([])
let counter = 0

export function showPush(
  msg: string,
  subKey: string = '',
  type: string = 'alert-info',
  icon: string = 'ri-box-3-line',
  autoclose: boolean = true,
) {
  const id = ++counter

  alerts.value.push({
    id,
    msg,
    subKey,
    type,
    icon,
  })

  if (autoclose) {
    setTimeout(() => {
      alerts.value = alerts.value.filter((a) => a.id !== id)
    }, lifetime)
  }
}
