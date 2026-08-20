import { Link, useParams } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import { data } from '../App'
import './ChapterPage.css'

type Panel = 'texto' | 'explicacao'

export function ChapterPage() {
  const { slug } = useParams()
  const index = data.chapters.findIndex((c) => c.slug === slug)
  const chapter = index >= 0 ? data.chapters[index] : null
  const prev = index > 0 ? data.chapters[index - 1] : null
  const next = index >= 0 && index < data.chapters.length - 1 ? data.chapters[index + 1] : null
  const [panel, setPanel] = useState<Panel>('texto')
  const [reveal, setReveal] = useState(0)

  useEffect(() => {
    setPanel('texto')
    setReveal(0)
  }, [slug])

  const progress = useMemo(() => {
    if (!chapter) return 0
    return Math.round(((index + 1) / data.chapters.length) * 100)
  }, [chapter, index])

  if (!chapter) {
    return (
      <div className="chapter missing">
        <h1>Capítulo não encontrado</h1>
        <Link to="/jornada">Voltar à jornada</Link>
      </div>
    )
  }

  const visibleParas = chapter.paragraphs.slice(0, Math.max(4, reveal || chapter.paragraphs.length))
  const canRevealMore = reveal > 0 && reveal < chapter.paragraphs.length

  return (
    <article className="chapter">
      <div className="chapter-progress" aria-hidden="true">
        <span style={{ width: `${progress}%` }} />
      </div>

      <header className="chapter-head">
        <p className="eyebrow">
          Capítulo {String(chapter.id).padStart(2, '0')} · {progress}% da jornada
        </p>
        <h1>{chapter.title}</h1>
        {chapter.quote ? <p className="chapter-quote">“{chapter.quote}”</p> : null}
      </header>

      <div className="panel-switch" role="tablist" aria-label="Modo de leitura">
        <button
          role="tab"
          aria-selected={panel === 'texto'}
          className={panel === 'texto' ? 'active' : ''}
          onClick={() => setPanel('texto')}
        >
          Texto
        </button>
        <button
          role="tab"
          aria-selected={panel === 'explicacao'}
          className={panel === 'explicacao' ? 'active' : ''}
          onClick={() => setPanel('explicacao')}
        >
          Explicação
        </button>
      </div>

      <div className="chapter-grid">
        <section className={`panel text-panel ${panel === 'texto' ? 'show' : ''}`} aria-label="Texto do capítulo">
          <div className="prose">
            {(reveal === 0 ? chapter.paragraphs : visibleParas).map((para, i) => (
              <p key={i} style={{ animationDelay: `${Math.min(i, 8) * 40}ms` }}>
                {para}
              </p>
            ))}
          </div>
          {reveal === 0 && chapter.paragraphs.length > 8 ? (
            <button className="soft-btn" onClick={() => setReveal(6)}>
              Ler em etapas
            </button>
          ) : null}
          {canRevealMore ? (
            <button
              className="soft-btn"
              onClick={() => setReveal((n) => Math.min(n + 6, chapter.paragraphs.length))}
            >
              Continuar leitura
            </button>
          ) : null}
        </section>

        <aside className={`panel explain-panel ${panel === 'explicacao' ? 'show' : ''}`} aria-label="Explicação">
          <p className="explain-source">
            Leitura comentada · {data.meta.series.host} · {data.meta.series.channel}
          </p>
          <h2>Chave de leitura</h2>
          <p className="explain-summary">{chapter.explanation.summary}</p>
          <ul className="key-list">
            {chapter.explanation.keys.map((key) => (
              <li key={key}>{key}</li>
            ))}
          </ul>

          {chapter.videoId ? (
            <div className="video-block">
              <h3>Assistir ao comentário</h3>
              <div className="video-frame">
                <iframe
                  title={`Comentário: ${chapter.title}`}
                  src={`https://www.youtube-nocookie.com/embed/${chapter.videoId}`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  loading="lazy"
                />
              </div>
              <a className="video-link" href={chapter.videoUrl!} target="_blank" rel="noreferrer">
                Abrir no YouTube
              </a>
            </div>
          ) : (
            <p className="no-video">
              Este trecho enquadra a narrativa. Explore os capítulos temáticos com vídeos na{' '}
              <a href={data.meta.series.searchUrl} target="_blank" rel="noreferrer">
                série completa
              </a>
              .
            </p>
          )}
        </aside>
      </div>

      <nav className="chapter-nav" aria-label="Capítulos vizinhos">
        {prev ? (
          <Link to={`/capitulo/${prev.slug}`} className="nav-chip prev">
            <span>Anterior</span>
            <strong>{prev.title}</strong>
          </Link>
        ) : (
          <span />
        )}
        {next ? (
          <Link to={`/capitulo/${next.slug}`} className="nav-chip next">
            <span>Seguinte</span>
            <strong>{next.title}</strong>
          </Link>
        ) : (
          <Link to="/jornada" className="nav-chip next">
            <span>Fim do ciclo</span>
            <strong>Voltar ao mapa</strong>
          </Link>
        )}
      </nav>
    </article>
  )
}
