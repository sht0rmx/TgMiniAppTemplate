import apiClientInst from './api.ts'

export interface LanguageDto {
  id: string
  name: string
}

export class LanguagesService {
  private static readonly BASE = '/api/v1'

  static async getLanguages(): Promise<LanguageDto[]> {
    const response = await apiClientInst.get(`${this.BASE}/languages/list`)
    if (!Array.isArray(response.data.languages)) {
      return []
    }

    const languages = response.data.languages
      .map((item: any) => ({ id: String(item.id), name: String(item.name) })) as LanguageDto[]

    return languages.filter((language) => Boolean(language.id))
  }

  static async getLanguageMessages(locale: string): Promise<Record<string, any>> {
    const normalized = locale.split('-')[0]
    const response = await apiClientInst.get(`${this.BASE}/languages/get/${normalized}`)
    return response.data
  }
}
