import { useMusic } from './MusicContext'

export function MusicToggle() {
  const { playing, toggle } = useMusic()

  return (
    <button
      type="button"
      className={`music-toggle${playing ? ' on' : ''}`}
      onClick={toggle}
      aria-pressed={playing}
      aria-label={playing ? 'Desativar música' : 'Ativar música'}
      title={playing ? 'Desativar música' : 'Ativar música'}
    >
      <svg
        className="music-toggle-icon"
        viewBox="0 0 24 24"
        width="16"
        height="16"
        aria-hidden="true"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M9 18V5l12-2v13" />
        <circle cx="6" cy="18" r="3" />
        <circle cx="18" cy="16" r="3" />
        {!playing ? <path d="M2 2l20 20" /> : null}
      </svg>
      <span className="music-toggle-label">Música</span>
    </button>
  )
}
