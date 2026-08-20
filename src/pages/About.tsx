import { data } from '../App'
import './About.css'

export function About() {
  return (
    <div className="about">
      <header>
        <p className="eyebrow">Contexto</p>
        <h1>Sobre esta edição</h1>
      </header>

      <div className="about-grid">
        <section>
          <h2>A obra</h2>
          <p>
            Publicado em 1923, <em>O Profeta</em> de Khalil Gibran é prosa poética sobre os grandes eixos da
            vida humana. Al-Mustafa, após doze anos em Orphalese, parte — e só então a cidade pede a sua
            palavra.
          </p>
          <p>
            O texto apresentado foi extraído do arquivo <strong>O Profeta - Khalil Gibran.pdf</strong>, na
            tradução de Rafael Arrais (2013), revisada pelo Acordo Ortográfico.
          </p>
        </section>

        <section>
          <h2>As explicações</h2>
          <p>
            Cada capítulo inclui uma chave de leitura inspirada na série{' '}
            <strong>{data.meta.series.name}</strong>, apresentada por {data.meta.series.host} no canal{' '}
            {data.meta.series.channel}. Os vídeos estão embutidos quando disponíveis.
          </p>
          <p>
            <a href={data.meta.series.searchUrl} target="_blank" rel="noreferrer">
              Ver busca no canal Nova Acrópole →
            </a>
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
