import { Link } from 'react-router-dom'
import { data } from '../App'
import './Home.css'

export function Home() {
  const first = data.chapters[0]
  const featured = data.chapters.filter((c) => c.videoId).slice(0, 6)

  return (
    <div className="home">
      <section className="hero" aria-label="Apresentação">
        <div className="hero-veil" aria-hidden="true" />
        <div className="hero-content">
          <p className="hero-kicker">Orphalese · 12 anos · uma partida</p>
          <h1>O Profeta</h1>
          <p className="hero-lead">
            Khalil Gibran deixa Al-Mustafa falar sobre amor, trabalho, liberdade e morte — e a cidade só
            escuta quando o navio já chega.
          </p>
          <div className="hero-actions">
            <Link className="btn btn-primary" to={`/capitulo/${first.slug}`}>
              Começar a leitura
            </Link>
            <Link className="btn btn-ghost" to="/jornada">
              Ver a jornada
            </Link>
          </div>
        </div>
        <div className="hero-orbit" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
      </section>

      <section className="intro-band">
        <div className="intro-copy">
          <h2>Uma leitura que respira</h2>
          <p>
            Cada capítulo abre o texto de Gibran ao lado de uma explicação extraída do espírito da série
            comentada por Lúcia Helena Galvão no canal da Nova Acrópole — para ler nas entrelinhas, sem
            apressar a poesia.
          </p>
        </div>
        <blockquote>
          <p>“{data.chapters[1]?.quote || 'O amor não conhece limites…'}”</p>
          <cite>O Amor</cite>
        </blockquote>
      </section>

      <section className="featured">
        <div className="section-head">
          <h2>Capítulos com vídeo</h2>
          <Link to="/jornada">Abrir mapa completo →</Link>
        </div>
        <div className="featured-grid">
          {featured.map((chapter, i) => (
            <Link
              key={chapter.slug}
              to={`/capitulo/${chapter.slug}`}
              className="feat-card"
              style={{ animationDelay: `${i * 70}ms` }}
            >
              <span className="feat-num">{String(chapter.id).padStart(2, '0')}</span>
              <h3>{chapter.title}</h3>
              <p>{chapter.explanation.summary}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
