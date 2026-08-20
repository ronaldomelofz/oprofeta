import { Link, useParams } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import { data } from '../App'
import './ChapterPage.css'

type Panel = 'comentada' | 'texto' | 'video'

export function ChapterPage() {
  const { slug } = useParams()
  const index = data.chapters.findIndex((c) => c.slug === slug)
  const chapter = index >= 0 ? data.chapters[index] : null
  const prev = index > 0 ? data.chapters[index - 1] : null
  const next = index >= 0 && index < data.chapters.length - 1 ? data.chapters[index + 1] : null
  const [panel, setPanel] = useState<Panel>('comentada')

  useEffect(() => {
    setPanel('comentada')
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

  const commentary = chapter.commentary

  return (
    <article className="chapter">
      <div className="chapter-progress" aria-hidden="true">
        <span style={{ width: `${progress}%` }} />
      </div>

      <header className="chapter-head">
        <p className="eyebrow">
          Edição comentada · Capítulo {String(chapter.id).padStart(2, '0')} · {progress}%
        </p>
        <h1>{chapter.title}</h1>
        {chapter.quote ? <p className="chapter-quote">“{chapter.quote}”</p> : null}
        <p className="chapter-deck">{commentary.summary}</p>
      </header>

      <div className="panel-switch" role="tablist" aria-label="Modo de leitura">
        {(
          [
            ['comentada', 'Comentário'],
            ['texto', 'Texto'],
            ['video', 'Vídeo'],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            role="tab"
            aria-selected={panel === id}
            className={panel === id ? 'active' : ''}
            onClick={() => setPanel(id)}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="chapter-layout">
        <section
          className={`panel comment-panel ${panel === 'comentada' ? 'show' : ''}`}
          aria-label="Comentário filosófico"
        >
          <p className="explain-source">
            Leitura comentada · {data.meta.series.host} · {data.meta.series.channel}
          </p>

          <div className="essay">
            {commentary.sections.map((section) => (
              <section key={section.heading + section.body.slice(0, 24)} className="essay-block">
                <h2>{section.heading}</h2>
                <p>{section.body}</p>
              </section>
            ))}
          </div>

          {commentary.keys.length > 0 ? (
            <div className="keys-box">
              <h3>Chaves</h3>
              <ul>
                {commentary.keys.map((key) => (
                  <li key={key}>{key}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {commentary.reflections.length > 0 ? (
            <div className="reflect-box">
              <h3>Para refletir</h3>
              <ol>
                {commentary.reflections.map((q) => (
                  <li key={q}>{q}</li>
                ))}
              </ol>
            </div>
          ) : null}
        </section>

        <section className={`panel text-panel ${panel === 'texto' ? 'show' : ''}`} aria-label="Texto de Gibran">
          <h2 className="panel-title">Texto de Khalil Gibran</h2>
          <div className="prose">
            {chapter.paragraphs.map((para, i) => (
              <p key={i} style={{ animationDelay: `${Math.min(i, 8) * 35}ms` }}>
                {para}
              </p>
            ))}
          </div>
        </section>

        <section className={`panel video-panel ${panel === 'video' ? 'show' : ''}`} aria-label="Vídeo da série">
          <h2 className="panel-title">Palestra comentada</h2>
          {chapter.videoId ? (
            <>
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
                Abrir no YouTube →
              </a>
            </>
          ) : (
            <p className="no-video">
              Este capítulo enquadra a narrativa. Os temas centrais têm palestra na{' '}
              <a href={data.meta.series.searchUrl} target="_blank" rel="noreferrer">
                série completa
              </a>
              .
            </p>
          )}
        </section>
      </div>

      <div className="desktop-split" aria-hidden={false}>
        <div className="desktop-comment">
          <p className="explain-source">
            Leitura comentada · {data.meta.series.host}
          </p>
          <div className="essay">
            {commentary.sections.map((section) => (
              <section key={'d-' + section.heading + section.body.slice(0, 16)} className="essay-block">
                <h2>{section.heading}</h2>
                <p>{section.body}</p>
              </section>
            ))}
          </div>
          <div className="keys-box">
            <h3>Chaves</h3>
            <ul>
              {commentary.keys.map((key) => (
                <li key={'d-' + key}>{key}</li>
              ))}
            </ul>
          </div>
          <div className="reflect-box">
            <h3>Para refletir</h3>
            <ol>
              {commentary.reflections.map((q) => (
                <li key={'d-' + q}>{q}</li>
              ))}
            </ol>
          </div>
          {chapter.videoId ? (
            <div className="video-block">
              <h3>Assistir à palestra</h3>
              <div className="video-frame">
                <iframe
                  title={`Comentário desktop: ${chapter.title}`}
                  src={`https://www.youtube-nocookie.com/embed/${chapter.videoId}`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  loading="lazy"
                />
              </div>
            </div>
          ) : null}
        </div>
        <div className="desktop-text">
          <h2 className="panel-title">Texto de Khalil Gibran</h2>
          <div className="prose">
            {chapter.paragraphs.map((para, i) => (
              <p key={'dt-' + i}>{para}</p>
            ))}
          </div>
        </div>
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
