import { Link, useParams } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import { lettersData } from '../App'
import './ChapterPage.css'
import './Letters.css'

type Panel = 'texto' | 'comentada' | 'video'

export function LetterPage() {
  const { slug } = useParams()
  const index = lettersData.letters.findIndex((l) => l.slug === slug)
  const letter = index >= 0 ? lettersData.letters[index] : null
  const prev = index > 0 ? lettersData.letters[index - 1] : null
  const next =
    index >= 0 && index < lettersData.letters.length - 1 ? lettersData.letters[index + 1] : null
  const [panel, setPanel] = useState<Panel>('texto')
  const overview = lettersData.meta.commentary
  const video = lettersData.meta.video

  useEffect(() => {
    setPanel('texto')
  }, [slug])

  const progress = useMemo(() => {
    if (!letter) return 0
    return Math.round(((index + 1) / lettersData.letters.length) * 100)
  }, [letter, index])

  if (!letter) {
    return (
      <div className="chapter missing">
        <h1>Carta não encontrada</h1>
        <Link to="/cartas">Voltar às cartas</Link>
      </div>
    )
  }

  const note = letter.commentary

  const commentaryBlock = (
    <>
      <p className="explain-source">
        Leitura · {video.host} · {video.channel}
      </p>
      <div className="essay">
        <section className="essay-block">
          <h2>Esta carta</h2>
          <p>{note.summary}</p>
        </section>
        {overview.sections.slice(0, 2).map((section) => (
          <section key={section.heading} className="essay-block">
            <h2>{section.heading}</h2>
            <p>{section.body}</p>
          </section>
        ))}
      </div>
      {note.keys.length > 0 ? (
        <div className="keys-box">
          <h3>Chaves</h3>
          <ul>
            {note.keys.map((k) => (
              <li key={k}>{k}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {note.reflections.length > 0 ? (
        <div className="reflect-box">
          <h3>Para refletir</h3>
          <ol>
            {note.reflections.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ol>
        </div>
      ) : null}
      <div className="video-block">
        <h3>Palestra sobre a correspondência</h3>
        <div className="video-frame">
          <iframe
            title={video.title}
            src={`https://www.youtube-nocookie.com/embed/${video.id}`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            loading="lazy"
          />
        </div>
        <a className="video-link" href={video.url} target="_blank" rel="noreferrer">
          Abrir no YouTube →
        </a>
      </div>
      <p className="letter-overview-link">
        <Link to="/cartas">Ensaio completo sobre as cartas →</Link>
      </p>
    </>
  )

  const letterText = (
    <>
      <h2 className="panel-title">
        Texto íntegro · {letter.author}
        {letter.date ? ` · ${letter.date}` : ''}
      </h2>
      <div className="prose letter-prose">
        {letter.paragraphs.map((para, i) => (
          <p key={i} style={{ animationDelay: `${Math.min(i, 8) * 35}ms` }}>
            {para}
          </p>
        ))}
      </div>
    </>
  )

  return (
    <article className="chapter letter-page">
      <div className="chapter-progress" aria-hidden="true">
        <span style={{ width: `${progress}%` }} />
      </div>

      <header className="chapter-head">
        <p className="eyebrow">
          Cartas · {String(letter.id).padStart(2, '0')} · {letter.author}
          {letter.date ? ` · ${letter.date}` : ''} · {progress}%
        </p>
        <h1>{letter.title}</h1>
        <p className="chapter-deck">{note.summary}</p>
      </header>

      <div className="panel-switch" role="tablist" aria-label="Modo de leitura">
        {(
          [
            ['texto', 'Carta'],
            ['comentada', 'Comentário'],
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
        <section className={`panel text-panel ${panel === 'texto' ? 'show' : ''}`} aria-label="Texto da carta">
          {letterText}
        </section>
        <section
          className={`panel comment-panel ${panel === 'comentada' ? 'show' : ''}`}
          aria-label="Comentário filosófico"
        >
          {commentaryBlock}
        </section>
        <section className={`panel video-panel ${panel === 'video' ? 'show' : ''}`} aria-label="Palestra">
          <h2 className="panel-title">Palestra comentada</h2>
          <div className="video-frame">
            <iframe
              title={video.title}
              src={`https://www.youtube-nocookie.com/embed/${video.id}`}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              loading="lazy"
            />
          </div>
          <a className="video-link" href={video.url} target="_blank" rel="noreferrer">
            Abrir no YouTube →
          </a>
        </section>
      </div>

      <div className="desktop-split">
        <div className="desktop-comment">{commentaryBlock}</div>
        <div className="desktop-text">{letterText}</div>
      </div>

      <nav className="chapter-nav" aria-label="Navegação entre cartas">
        {prev ? (
          <Link to={`/cartas/${prev.slug}`} className="nav-chip prev">
            <span>Anterior</span>
            <strong>{prev.title}</strong>
          </Link>
        ) : (
          <span />
        )}
        {next ? (
          <Link to={`/cartas/${next.slug}`} className="nav-chip next">
            <span>Seguinte</span>
            <strong>{next.title}</strong>
          </Link>
        ) : (
          <Link to="/cartas" className="nav-chip next">
            <span>Fim</span>
            <strong>Todas as cartas</strong>
          </Link>
        )}
      </nav>
    </article>
  )
}
