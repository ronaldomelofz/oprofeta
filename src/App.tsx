import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
import { ChapterPage } from './pages/ChapterPage'
import { Journey } from './pages/Journey'
import { About } from './pages/About'
import book from './data/chapters.json'
import type { BookData } from './types'

export const data = book as BookData

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="jornada" element={<Journey />} />
        <Route path="capitulo/:slug" element={<ChapterPage />} />
        <Route path="sobre" element={<About />} />
      </Route>
    </Routes>
  )
}
