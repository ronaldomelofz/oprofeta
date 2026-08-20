export interface CommentarySection {
  heading: string
  body: string
}

export interface ChapterCommentary {
  summary: string
  sections: CommentarySection[]
  keys: string[]
  reflections: string[]
}

export interface ChapterExplanation {
  summary: string
  keys: string[]
}

export interface Chapter {
  id: number
  slug: string
  title: string
  paragraphs: string[]
  commentary: ChapterCommentary
  explanation: ChapterExplanation
  videoId: string | null
  videoUrl: string | null
  quote: string
}

export interface BookMeta {
  title: string
  subtitle?: string
  author: string
  translator: string
  year: number
  edition?: string
  series: {
    name: string
    host: string
    channel: string
    channelUrl: string
    searchUrl: string
  }
  note: string
  sources?: {
    textPdf: string
    textPdfAlt?: string
    series: BookMeta['series']
  }
}

export interface BookData {
  meta: BookMeta
  chapters: Chapter[]
}
