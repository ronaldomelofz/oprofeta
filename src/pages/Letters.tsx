import { Link } from 'react-router-dom'
import { lettersData } from '../App'
import './Journey.css'
import './ChapterPage.css'
import './Letters.css'

export function Letters() {
  const { meta, letters } = lettersData
  const overview = meta.commentary

  return (
    <div className="journey letters-page">
      <header className="journey-head">
        <p className="eyebrow">Correspondência comentada</p>
        <h1>{meta.title}</h1>
        <p>
          {meta.subtitle}. Comentário a partir da palestra <em>O Grande Amor do Profeta</em> (
          {meta.video.host}, {meta.video.channel}, 2009).
        </p>
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
        <h2>{letters.length} momentos da correspondência</h2>
        <p>{meta.note}</p>
      </header>

      <ol className="journey-list">
        {letters.map((letter, index) => (
          <li key={letter.slug} style={{ animationDelay: `${Math.min(index, 12) * 40}ms` }}>
            <Link to={`/cartas/${letter.slug}`} className="journey-item">
              <span className="journey-index">{String(letter.id).padStart(2, '0')}</span>
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
