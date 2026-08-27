import { Link } from 'react-router-dom'
import { useMemo, useState } from 'react'
import { lettersData } from '../App'
import './Journey.css'
import './ChapterPage.css'
import './Letters.css'

function yearOf(date: string | null): string {
  if (!date) return 'sem-data'
  const m = date.match(/(19[0-3]\d)/)
  return m ? m[1] : 'sem-data'
}

export function Letters() {
  const { meta, letters } = lettersData
  const overview = meta.commentary
  const [author, setAuthor] = useState<'todas' | 'Gibran' | 'Mary'>('todas')
  const [year, setYear] = useState<string>('todas')

  const years = useMemo(() => {
    const set = new Set<string>()
    for (const l of letters) {
      const y = yearOf(l.date)
      if (y !== 'sem-data') set.add(y)
    }
    return Array.from(set).sort()
  }, [letters])

  const filtered = useMemo(() => {
    return letters.filter((l) => {
      if (author !== 'todas' && l.author !== author) return false
      if (year !== 'todas' && yearOf(l.date) !== year) return false
      return true
    })
  }, [letters, author, year])

  return (
    <div className="journey letters-page">
      <header className="journey-head">
        <p className="eyebrow">Correspondência comentada</p>
        <h1>{meta.title}</h1>
        <p>
          {meta.subtitle}. Comentário a partir da palestra <em>O Grande Amor do Profeta</em> (
          {meta.video.host}, {meta.video.channel}, 2009).
        </p>
        {meta.sourcePdf && (
          <p className="letters-edition">
            Edição integral:{' '}
            <a href={meta.sourcePdf} target="_blank" rel="noreferrer">
              Profeta Amado — PDF em português
            </a>
            {meta.sourceEdition ? (
              <>
                {' '}
                <span className="letters-edition-source">(fonte: {meta.sourceEdition})</span>
              </>
            ) : null}
          </p>
        )}
      </header>

      <section className="letters-overview">
        <p className="letters-overview-summary">{overview.summary}</p>
        <div className="letters-video">
          <iframe
            title={meta.video.title}
            src={`https://www.youtube.com/embed/${meta.video.id}`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
          <p>
            <a href={meta.video.url} target="_blank" rel="noreferrer">
              Abrir a palestra no YouTube →
            </a>
          </p>
        </div>
        <div className="essay letters-essay">
          {overview.sections.map((section) => (
            <section key={section.heading}>
              <h2>{section.heading}</h2>
              <p>{section.body}</p>
            </section>
          ))}
        </div>
        <div className="keys-block">
          <h3>Chaves</h3>
          <ul>
            {overview.keys.map((k) => (
              <li key={k}>{k}</li>
            ))}
          </ul>
        </div>
      </section>

      <header className="journey-head letters-list-head">
        <p className="eyebrow">As cartas</p>
        <h2>
          {filtered.length === letters.length
            ? `${letters.length} cartas da correspondência`
            : `${filtered.length} de ${letters.length} cartas`}
        </h2>
        <p>{meta.note}</p>
      </header>

      <div className="letters-filters" role="group" aria-label="Filtrar cartas">
        <label>
          Autor
          <select value={author} onChange={(e) => setAuthor(e.target.value as typeof author)}>
            <option value="todas">Todas</option>
            <option value="Gibran">Gibran</option>
            <option value="Mary">Mary</option>
          </select>
        </label>
        <label>
          Ano
          <select value={year} onChange={(e) => setYear(e.target.value)}>
            <option value="todas">Todos</option>
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
            <option value="sem-data">Sem data</option>
          </select>
        </label>
      </div>

      <ol className="journey-list">
        {filtered.map((letter, index) => (
          <li key={letter.slug} style={{ animationDelay: `${Math.min(index, 12) * 40}ms` }}>
            <Link to={`/cartas/${letter.slug}`} className="journey-item">
              <span className="journey-index">{String(letter.id).padStart(3, '0')}</span>
              <div className="journey-body">
                <h2>
                  {letter.title}
                  <span className="letter-author"> · {letter.author}</span>
                </h2>
                <p>{letter.commentary?.summary || letter.quote}</p>
              </div>
              <span className="journey-meta">
                {letter.date || 'Sem data'}
                <span aria-hidden="true">→</span>
              </span>
            </Link>
          </li>
        ))}
      </ol>
    </div>
  )
}
