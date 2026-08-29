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
          <p className="hero-kicker">Edição comentada · Nova Acrópole</p>
          <h1>O Profeta</h1>
          <p className="hero-lead">
            Khalil Gibran, capítulo a capítulo — o texto integral ao lado da leitura filosófica da
            Professora Lúcia Helena Galvão, para abrir as entrelinhas do poema.
          </p>
          <div className="hero-actions">
            <Link className="btn btn-primary" to={`/capitulo/${first.slug}`}>
              Abrir a edição
            </Link>
            <Link className="btn btn-ghost" to="/jornada">
              Mapa dos capítulos
            </Link>
            <Link className="btn btn-ghost" to="/cartas">
              Cartas de amor
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
          <h2>Uma obra comentada</h2>
          <p>
            Cada capítulo reúne o poema de Gibran, um comentário destilado das palestras da série e o vídeo
            original no canal da Nova Acrópole. Ler aqui é acompanhar o Profeta com uma chave filosófica em
            mãos.
          </p>
        </div>
        <blockquote>
          <p>“{data.chapters[1]?.quote || 'Quando o amor lhes acenar, sigam-no…'}”</p>
          <cite>O amor</cite>
        </blockquote>
      </section>

      <section className="featured">
        <div className="section-head">
          <h2>Comece por estes</h2>
          <Link to="/jornada">Ver os 28 capítulos →</Link>
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
              <p>{chapter.commentary?.summary || chapter.explanation.summary}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
