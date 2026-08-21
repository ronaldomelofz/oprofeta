import { data, lettersData } from '../App'
import './About.css'

export function About() {
  return (
    <div className="about">
      <header>
        <p className="eyebrow">Contexto</p>
        <h1>Sobre esta edição comentada</h1>
      </header>

      <div className="about-grid">
        <section>
          <h2>O texto</h2>
          <p>
            Publicado em 1923, <em>O Profeta</em> de Khalil Gibran é prosa poética sobre os eixos da vida
            humana.
          </p>
        </section>

        <section>
          <h2>O comentário</h2>
          <p>
            Cada capítulo inclui uma leitura filosófica destilada das palestras de{' '}
            {data.meta.series.host} na série <strong>{data.meta.series.name}</strong> ({' '}
            {data.meta.series.channel}). Os vídeos originais estão embutidos sempre que disponíveis.
          </p>
          <p>
            <a href={data.meta.series.searchUrl} target="_blank" rel="noreferrer">
              Ver a série no YouTube →
            </a>
          </p>
        </section>

        <section>
          <h2>As cartas</h2>
          <p>
            A seção <em>Cartas</em> reúne a correspondência condensada entre Gibran e Mary Haskell, com
            comentário a partir da palestra{' '}
            <a href={lettersData.meta.video.url} target="_blank" rel="noreferrer">
              {lettersData.meta.video.title}
            </a>
            . No canal da Nova Acrópole não há série carta a carta — esta homenagem de 2009 é a referência
            principal encontrada sobre o tema.
          </p>
        </section>

        <section>
          <h2>Créditos</h2>
          <ul>
            <li>Autor: Khalil Gibran</li>
            <li>Tradução de referência: Rafael Arrais (2013)</li>
            <li>Comentários de referência: Lúcia Helena Galvão / Nova Acrópole Brasil</li>
            <li>
              Publicação: <a href="https://oprofetagibran.netlify.app/">oprofetagibran.netlify.app</a>
            </li>
          </ul>
        </section>
      </div>
    </div>
  )
}
