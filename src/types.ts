export interface ChapterExplanation {
  summary: string
  keys: string[]
}

export interface Chapter {
  id: number
  slug: string
  title: string
  paragraphs: string[]
  explanation: ChapterExplanation
  videoId: string | null
  videoUrl: string | null
  quote: string
}

export interface BookMeta {
  title: string
  author: string
  translator: string
  year: number
  series: {
    name: string
    host: string
    channel: string
    channelUrl: string
    searchUrl: string
  }
  note: string
}

export interface BookData {
  meta: BookMeta
  chapters: Chapter[]
}
