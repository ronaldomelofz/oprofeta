import { Link, useParams } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import { lettersData } from '../App'
import './ChapterPage.css'
import './Letters.css'

type Panel = 'comentada' | 'texto' | 'video'

export function LetterPage() {
  const { slug } = useParams()
  const index = lettersData.letters.findIndex((l) => l.slug === slug)
  const letter = index >= 0 ? lettersData.letters[index] : null
  const prev = index > 0 ? lettersData.letters[index - 1] : null
  const next =
    index >= 0 && index < lettersData.letters.length - 1 ? lettersData.letters[index + 1] : null
  const [panel, setPanel] = useState<Panel>('comentada')
  const overview = lettersData.meta.commentary
  const video = lettersData.meta.video

  useEffect(() => {
    setPanel('comentada')
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
        {letter.quote ? <p className="chapter-quote">“{letter.quote}”</p> : null}
        <p className="chapter-deck">{note.summary}</p>
      </header>

      <div className="panel-switch" role="tablist" aria-label="Modo de leitura">
        {(
          [
            ['comentada', 'Comentário'],
            ['texto', 'Carta'],
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
            Leitura · {video.host} · {video.channel} · palestra {video.title}
          </p>

          <div className="essay">
            <section>
              <h2>Esta carta</h2>
              <p>{note.summary}</p>
            </section>
            {overview.sections.slice(0, 2).map((section) => (
              <section key={section.heading}>
                <h2>{section.heading}</h2>
                <p>{section.body}</p>
              </section>
            ))}
          </div>

          <div className="keys-block">
            <h3>Chaves</h3>
            <ul>
              {note.keys.map((k) => (
                <li key={k}>{k}</li>
              ))}
            </ul>
          </div>

          <div className="reflect-block">
            <h3>Para refletir</h3>
            <ul>
              {note.reflections.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
          </div>

          <p className="letter-overview-link">
            <Link to="/cartas">Ler o ensaio completo sobre a correspondência →</Link>
          </p>
        </section>

        <section
          className={`panel text-panel ${panel === 'texto' ? 'show' : ''}`}
          aria-label="Texto da carta"
        >
          <div className="prose letter-prose">
            {letter.paragraphs.map((p, i) => (
              <p key={i}>{p}</p>
            ))}
          </div>
        </section>

        <section
          className={`panel video-panel ${panel === 'video' ? 'show' : ''}`}
          aria-label="Palestra"
        >
          <div className="video-frame">
            <iframe
              title={video.title}
              src={`https://www.youtube.com/embed/${video.id}`}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
          <p className="video-caption">
            Palestra única encontrada no canal sobre as cartas:{' '}
            <a href={video.url} target="_blank" rel="noreferrer">
              {video.title}
            </a>
            . Não há série carta a carta; o comentário desta edição destila essa homenagem de 2009.
          </p>
        </section>
      </div>

      <nav className="chapter-nav" aria-label="Navegação entre cartas">
        {prev ? (
          <Link to={`/cartas/${prev.slug}`} className="nav-prev">
            <span>Anterior</span>
            <strong>{prev.title}</strong>
          </Link>
        ) : (
          <span />
        )}
        <Link to="/cartas" className="nav-map">
          Todas as cartas
        </Link>
        {next ? (
          <Link to={`/cartas/${next.slug}`} className="nav-next">
            <span>Próxima</span>
            <strong>{next.title}</strong>
          </Link>
        ) : (
          <span />
        )}
      </nav>
    </article>
  )
}
