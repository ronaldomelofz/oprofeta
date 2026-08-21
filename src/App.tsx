import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
import { ChapterPage } from './pages/ChapterPage'
import { Journey } from './pages/Journey'
import { Letters } from './pages/Letters'
import { LetterPage } from './pages/LetterPage'
import { About } from './pages/About'
import book from './data/chapters.json'
import letters from './data/letters.json'
import type { BookData, LettersData } from './types'

export const data = book as BookData
export const lettersData = letters as LettersData

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="jornada" element={<Journey />} />
        <Route path="capitulo/:slug" element={<ChapterPage />} />
        <Route path="cartas" element={<Letters />} />
        <Route path="cartas/:slug" element={<LetterPage />} />
        <Route path="sobre" element={<About />} />
      </Route>
    </Routes>
  )
}
