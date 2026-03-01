import apiClientInst from './api.ts'

export interface FileItem {
  id: string
  name: string
  key: string
  uploadedAt: string
}

export interface AllFilesResponse {
  files: FileItem[]
}

export class FilesService {
  private static BASE = '/api/v1/files'

  static async getAll(): Promise<FileItem[]> {
    try {
      const res = await apiClientInst.get(`${this.BASE}/all`)
      if (res.status === 200) {
        return (res.data as AllFilesResponse).files
      }
      return []
    } catch {
      return []
    }
  }

  static async upload(file: File): Promise<boolean> {
    try {
      const form = new FormData()
      form.append('file', file)

      const res = await apiClientInst.post(`${this.BASE}/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000,
      })
      return res.status === 201
    } catch {
      return false
    }
  }

  static async download(fileId: string, fileName: string): Promise<boolean> {
    try {
      const res = await apiClientInst.get(`${this.BASE}/${fileId}`, {
        responseType: 'blob',
      })
      if (res.status === 200) {
        const url = URL.createObjectURL(res.data)
        const a = document.createElement('a')
        a.href = url
        a.download = fileName
        a.click()
        URL.revokeObjectURL(url)
        return true
      }
      return false
    } catch {
      return false
    }
  }

  static async getBlob(fileId: string): Promise<Blob | null> {
    try {
      const res = await apiClientInst.get(`${this.BASE}/${fileId}`, {
        responseType: 'blob',
      })
      return res.status === 200 ? res.data : null
    } catch {
      return null
    }
  }

  static async remove(fileId: string): Promise<boolean> {
    try {
      const res = await apiClientInst.delete(`${this.BASE}/${fileId}`)
      return res.status === 200
    } catch {
      return false
    }
  }
}
