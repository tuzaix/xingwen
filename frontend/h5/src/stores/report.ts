import { defineStore } from 'pinia'

interface ReportState {
  currentReportId: string | null
  reportContent: string | null
  isGenerating: boolean
  status: 'idle' | 'generating' | 'completed' | 'failed'
  error: string | null
}

export const useReportStore = defineStore('report', {
  state: (): ReportState => ({
    currentReportId: null,
    reportContent: null,
    isGenerating: false,
    status: 'idle',
    error: null
  }),
  actions: {
    setReport(id: string, content: string) {
      this.currentReportId = id
      this.reportContent = content
      this.status = 'completed'
    },
    setGenerating(isGenerating: boolean) {
      this.isGenerating = isGenerating
      this.status = isGenerating ? 'generating' : 'idle'
    },
    setError(error: string) {
      this.error = error
      this.status = 'failed'
    }
  }
})
