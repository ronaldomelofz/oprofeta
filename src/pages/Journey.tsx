import { Link } from 'react-router-dom'
import { data } from '../App'
import './Journey.css'

export function Journey() {
  return (
    <div className="journey">
      <header className="journey-head">
        <p className="eyebrow">Mapa da edição comentada</p>
        <h1>A jornada em Orphalese</h1>
        <p>
          Vinte e oito momentos — da chegada do navio à despedida. Em cada um: o texto de Gibran, o
          comentário filosófico e, quando existe, a palestra da série Nova Acrópole.
        </p>
      </header>

      <ol className="journey-list">
        {data.chapters.map((chapter, index) => (
          <li key={chapter.slug} style={{ animationDelay: `${Math.min(index, 12) * 40}ms` }}>
            <Link to={`/capitulo/${chapter.slug}`} className="journey-item">
              <span className="journey-index">{String(chapter.id).padStart(2, '0')}</span>
              <div className="journey-body">
                <h2>{chapter.title}</h2>
                <p>{chapter.commentary?.summary || chapter.explanation.summary}</p>
              </div>
              <span className="journey-meta">
                {chapter.videoId ? 'Texto + vídeo' : 'Texto'}
                <span aria-hidden="true">→</span>
              </span>
            </Link>
          </li>
        ))}
      </ol>
    </div>
  )
}
