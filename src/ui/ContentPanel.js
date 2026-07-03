import about from '../data/about.json';
import projects from '../data/projects.json';
import skills from '../data/skills.json';
import experience from '../data/experience.json';
import certifications from '../data/certifications.json';
import resume from '../data/resume.json';
import contact from '../data/contact.json';
import { openLightbox } from './Lightbox.js';
import { playClickSound } from './uiSound.js';

const overlay = document.getElementById('content-overlay');
const panelHeader = document.getElementById('content-header');
const panelBody = document.getElementById('content-body');
const closeBtn = document.getElementById('content-close');

let onCloseCallback = null;

function esc(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function header(eyebrow, title, subtitle) {
  panelHeader.innerHTML = `
    <span class="eyebrow">${esc(eyebrow)}</span>
    <h1>${esc(title)}</h1>
    ${subtitle ? `<p>${esc(subtitle)}</p>` : ''}
  `;
}

const CATEGORY_COLOR = {
  Internship: '#3f6fb0',
  Research: '#2c8f8f',
  Achievement: '#c98a2c',
  Leadership: '#b0477a',
};

const RENDERERS = {
  projects: () => {
    header('Projects', `${about.name}\u2019s Projects`, `${projects.length} projects — click a card for details`);
    panelBody.innerHTML = `
      <div class="card-grid">
        ${projects
          .map(
            (p, i) => `
          <div class="card project-card" data-index="${i}">
            <h3>${esc(p.title)}</h3>
            <p>${esc(p.description)}</p>
            <div class="tag-row">${p.tech.map((t) => `<span class="tag">${esc(t)}</span>`).join('')}</div>
            <div class="card-actions">
              ${p.github ? `<a class="btn-mini" href="${esc(p.github)}" target="_blank" rel="noopener" data-stop>GitHub ↗</a>` : ''}
              ${p.demo ? `<a class="btn-mini btn-mini-accent" href="${esc(p.demo)}" target="_blank" rel="noopener" data-stop>Live Demo ↗</a>` : ''}
            </div>
          </div>`
          )
          .join('')}
      </div>
    `;
    panelBody.querySelectorAll('.project-card').forEach((card) => {
      card.addEventListener('click', (e) => {
        if (e.target.closest('[data-stop]')) return;
        playClickSound();
        const p = projects[Number(card.dataset.index)];
        openLightbox(`
          <h2 style="margin:0 0 6px;">${esc(p.title)}</h2>
          <p style="color:var(--color-text-dim);font-size:14px;line-height:1.6;">${esc(p.description)}</p>
          <div class="tag-row" style="margin:12px 0;">${p.tech.map((t) => `<span class="tag">${esc(t)}</span>`).join('')}</div>
          <div class="card-actions">
            ${p.github ? `<a class="btn-mini" href="${esc(p.github)}" target="_blank" rel="noopener">View on GitHub ↗</a>` : ''}
            ${p.demo ? `<a class="btn-mini btn-mini-accent" href="${esc(p.demo)}" target="_blank" rel="noopener">Live Demo ↗</a>` : ''}
          </div>
        `);
      });
    });
  },

  resume: () => {
    header('Resume', 'Resume', resume.summary);
    panelBody.innerHTML = `
      <div class="resume-actions">
        <a class="btn-primary" href="${esc(resume.downloadUrl)}" download>⬇ Download Resume</a>
        <a class="btn-secondary" href="${esc(resume.viewUrl)}" target="_blank" rel="noopener">👁 View Full Resume</a>
      </div>
      <div class="resume-preview">
        <iframe src="${esc(resume.viewUrl)}" title="Resume preview" loading="lazy"></iframe>
      </div>
      <div class="skill-group">
        <h3>Experience</h3>
        ${resume.experience
          .map(
            (i) => `
          <div class="timeline-item">
            <div class="timeline-dot" style="background:#2c8f8f"></div>
            <div>
              <h3>${esc(i.role)}${i.org ? ` · ${esc(i.org)}` : ''}</h3>
              <div class="meta">${esc(i.period)}</div>
              ${i.detail ? `<p>${esc(i.detail)}</p>` : ''}
            </div>
          </div>`
          )
          .join('')}
      </div>
      <div class="skill-group">
        <h3>Education</h3>
        ${resume.education
          .map(
            (i) => `
          <div class="timeline-item">
            <div class="timeline-dot" style="background:#2c8f8f"></div>
            <div>
              <h3>${esc(i.role)}${i.org ? ` · ${esc(i.org)}` : ''}</h3>
              <div class="meta">${esc(i.period)}</div>
            </div>
          </div>`
          )
          .join('')}
      </div>
    `;
  },

  skills: () => {
    header('Skills', 'Skills & Tools');
    panelBody.innerHTML = skills.groups
      .map(
        (group) => `
      <div class="skill-group">
        <h3>${esc(group.name)}</h3>
        <div class="skill-icon-grid">
          ${group.items
            .map(
              (item) => `
            <div class="skill-icon-card">
              <div class="skill-icon">${item.icon}</div>
              <div class="skill-icon-name">${esc(item.name)}</div>
              <div class="skill-bar-track"><div class="skill-bar-fill" style="width:${item.level}%"></div></div>
            </div>`
            )
            .join('')}
        </div>
      </div>`
      )
      .join('');
  },

  experience: () => {
    header('Experience', 'Experience & Journey', 'Internships · research · achievements · leadership');
    panelBody.innerHTML = experience.timeline
      .map(
        (item) => `
      <div class="timeline-item">
        <div class="timeline-dot" style="background:${CATEGORY_COLOR[item.category] || '#3f6fb0'}"></div>
        <div>
          <span class="tag" style="margin-bottom:6px;display:inline-block;">${esc(item.category)}</span>
          <h3>${esc(item.title)}${item.org ? ` · ${esc(item.org)}` : ''}</h3>
          <div class="meta">${esc(item.period)}</div>
          <p>${esc(item.detail)}</p>
        </div>
      </div>`
      )
      .join('');
  },

  certifications: () => {
    header('Certifications', 'Certifications', `${certifications.length} credentials — click to view details`);
    panelBody.innerHTML = `
      <div class="card-grid">
        ${certifications
          .map(
            (c, i) => `
          <div class="card cert-card" data-index="${i}">
            <div class="cert-badge">🎖️</div>
            <h3>${esc(c.title)}</h3>
            <p>${esc(c.issuer)} · ${esc(c.date)}</p>
          </div>`
          )
          .join('')}
      </div>
    `;
    panelBody.querySelectorAll('.cert-card').forEach((card) => {
      card.addEventListener('click', () => {
        playClickSound();
        const c = certifications[Number(card.dataset.index)];
        openLightbox(`
          <div class="cert-badge" style="font-size:48px;">🎖️</div>
          <h2 style="margin:10px 0 4px;">${esc(c.title)}</h2>
          <p style="color:var(--color-text-dim);margin:0 0 10px;">${esc(c.issuer)} · ${esc(c.date)}</p>
          <p style="font-size:14px;line-height:1.6;">${esc(c.detail)}</p>
          ${c.link ? `<a class="btn-mini" href="${esc(c.link)}" target="_blank" rel="noopener">View credential ↗</a>` : ''}
        `);
      });
    });
  },

  contact: () => {
    header('Contact', 'Let\u2019s Connect', `${contact.location}`);
    panelBody.innerHTML = `
      <div class="contact-list">
        ${contact.links
          .map(
            (l) => `
          <a class="contact-row" href="${esc(l.href)}" target="_blank" rel="noopener">
            <span class="contact-icon">${l.icon || ''}</span>
            <div>
              <div class="label">${esc(l.label)}</div>
              <div class="value">${esc(l.value)}</div>
            </div>
          </a>`
          )
          .join('')}
      </div>
    `;
  },

  education: () => {
    header('Education', 'Education', 'Degrees & coursework');
    panelBody.innerHTML = `
      <div class="skill-group">
        ${resume.education
          .map(
            (i) => `
          <div class="timeline-item">
            <div class="timeline-dot" style="background:#1f4e9c"></div>
            <div>
              <h3>${esc(i.role)}${i.org ? ` · ${esc(i.org)}` : ''}</h3>
              <div class="meta">${esc(i.period)}</div>
              ${i.detail ? `<p>${esc(i.detail)}</p>` : ''}
            </div>
          </div>`
          )
          .join('')}
      </div>
    `;
  },

  about: () => {
    header('About Me', `${about.name}`, `${about.role} · ${about.location}`);
    panelBody.innerHTML = `
      <p style="line-height:1.7;color:var(--color-text-dim);margin:0 0 16px;">${esc(about.bio || '')}</p>
      <div class="card-grid">
        ${(about.highlights || [])
          .map(
            (h) => `
          <div class="card">
            <div style="font-size:22px;margin-bottom:6px;">${h.icon || ''}</div>
            <h3 style="margin:0 0 2px;">${esc(h.label)}</h3>
            <p style="margin:0;">${esc(h.value)}</p>
          </div>`
          )
          .join('')}
      </div>
    `;
  },

  research: () => {
    const items = experience.timeline.filter((i) => i.category === 'Research');
    header('Research', 'Research', `${items.length ? items.length + ' item' + (items.length > 1 ? 's' : '') : 'Papers & findings'}`);
    panelBody.innerHTML = items.length
      ? items
          .map(
            (item) => `
      <div class="timeline-item">
        <div class="timeline-dot" style="background:#0f4c4c"></div>
        <div>
          <span class="tag" style="margin-bottom:6px;display:inline-block;">${esc(item.category)}</span>
          <h3>${esc(item.title)}${item.org ? ` · ${esc(item.org)}` : ''}</h3>
          <div class="meta">${esc(item.period)}</div>
          <p>${esc(item.detail)}</p>
        </div>
      </div>`
          )
          .join('')
      : `<p style="color:var(--color-text-dim);">More research write-ups coming soon.</p>`;
  },
};

export function openSection(key) {
  const renderer = RENDERERS[key];
  if (!renderer) return;
  renderer();
  overlay.classList.remove('hidden');
  playClickSound();
}

export function closeSection() {
  overlay.classList.add('hidden');
  if (onCloseCallback) onCloseCallback();
}

export function isOpen() {
  return !overlay.classList.contains('hidden');
}

export function onClose(cb) {
  onCloseCallback = cb;
}

closeBtn.addEventListener('click', () => {
  playClickSound();
  closeSection();
});
overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closeSection();
});
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && isOpen()) closeSection();
});
