import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import './Layout.css'

export function Layout() {
  const location = useLocation()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location.pathname])

  return (
    <div className="shell">
      <header className="topbar">
        <NavLink to="/" className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <span className="brand-text">
            <strong>O Profeta</strong>
            <em>Edição comentada</em>
          </span>
        </NavLink>
        <nav className="nav" aria-label="Principal">
          <NavLink to="/" end>
            Início
          </NavLink>
          <NavLink to="/jornada">Jornada</NavLink>
          <NavLink to="/sobre">Sobre</NavLink>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="footer">
        <p>
          O Profeta comentado · Khalil Gibran · chaves de leitura inspiradas na série da{' '}
          <a href="https://www.youtube.com/@NovaAcropole" target="_blank" rel="noreferrer">
            Nova Acrópole
          </a>
        </p>
      </footer>
    </div>
  )
}
