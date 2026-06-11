<template>
  <div class="dashboard">
    <header class="header">
      <div class="logo">
        <div class="logo-icon">FL</div>
        <div>
          <div class="logo-text">FanLens</div>
          <div class="logo-sub">Theory Intelligence</div>
        </div>
      </div>
      <div class="header-right">
        <input v-model="search" placeholder="Search theories..." class="search-box" />
        <div class="sort-btns">
          <button v-for="s in sorts" :key="s" :class="['sort-btn', { active: sort === s }]" @click="sort = s">{{ s }}</button>
        </div>
      </div>
    </header>

    <div v-if="toast" class="toast">{{ toast }}</div>

    <div class="layout">
      <div class="feed">

        <!-- AI Theory Generator -->
        <div class="generator-card">
          <div class="generator-title">🤖 AI Theory Generator</div>
          <div class="generator-sub">Pick a fandom and let AI create an original fan theory</div>
          <div class="generator-controls">
            <select v-model="genSubreddit" class="gen-select">
              <option value="">Select subreddit...</option>
              <option v-for="sub in subreddits" :key="sub.name" :value="sub.name">r/{{ sub.name }}</option>
            </select>
            <button class="gen-btn" @click="generateTheory" :disabled="!genSubreddit || generating">
              {{ generating ? '✨ Generating...' : '✨ Generate' }}
            </button>
          </div>
          <div v-if="generatedTheory" class="gen-result">
            <div class="gen-text">{{ generatedTheory }}</div>
            <button class="gen-clear" @click="generatedTheory = ''">✕</button>
          </div>
        </div>

        <div class="confidence-filter">
          <button v-for="c in confidenceFilters" :key="c" :class="['conf-btn', { active: confidenceFilter === c }]" @click="setConfidenceFilter(c)">{{ c }}</button>
        </div>

        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          Loading theories...
        </div>
        <div v-else-if="filteredTheories.length === 0" class="empty">No theories found.</div>
        <div
          v-for="theory in filteredTheories"
          :key="theory._id"
          class="theory-card"
          :style="{ borderLeftColor: theory.confidence === 'high' ? '#28a745' : theory.confidence === 'medium' ? '#ffc107' : '#dc3545' }"
          @click="openTheory(theory)"
        >
          <div class="card-top">
            <div class="card-title">{{ theory.title }}</div>
            <span :class="['badge', confidenceClass(theory.confidence)]">{{ theory.confidence || 'unrated' }}</span>
          </div>
          <div class="card-body">{{ stripHtml(theory.body).slice(0, 200) }}...</div>
          <div class="card-meta">
            <span>↑ {{ theory.upvotes }}</span>
            <span>💬 {{ theory.comment_count }}</span>
            <span class="sub-tag">r/{{ theory.subreddit }}</span>
            <button class="share-btn" @click.stop="shareTheory(theory)">🔗 share</button>
            <a :href="theory.url" target="_blank" class="view-link" @click.stop>view post</a>
          </div>
        </div>

        <button v-if="hasMore && !loading" class="load-more" @click="loadMore">Load more</button>
      </div>

      <div class="sidebar">
        <div class="sidebar-section">
          <div class="sidebar-title">Subreddits</div>
          <div
            v-for="sub in subreddits"
            :key="sub.name"
            :class="['sub-chip', { active: activeSub === sub.name }]"
            @click="toggleSub(sub.name)"
          >
            r/{{ sub.name }} <span class="sub-count">{{ sub.count }}</span>
            <span class="sub-delete" @click.stop="deleteSubreddit(sub.name)">✕</span>
          </div>
          <div class="sub-chip add-chip" @click="addSubreddit">+ add subreddit</div>
        </div>

        <div class="sidebar-section" style="margin-top: 16px;">
          <div class="sidebar-title">Topic Clusters</div>
          <div v-for="cluster in clusters" :key="cluster._id" class="cluster-item">
            <span class="cluster-label">{{ cluster._id }}</span>
            <span class="cluster-count">{{ cluster.count }}</span>
          </div>
        </div>

        <div class="sidebar-section" style="margin-top: 16px;">
          <div class="sidebar-title">🔥 Trending Now</div>
          <div v-if="trending.length === 0" class="empty-small">No recent activity</div>
          <div v-for="t in trending" :key="t._id" class="trending-item" @click="openTheory(t)">
            <div class="trending-title">{{ t.title }}</div>
            <span class="sub-tag" style="font-size: 11px;">r/{{ t.subreddit }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedTheory" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">{{ selectedTheory.title }}</div>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <div class="modal-meta">
          <span :class="['badge', confidenceClass(selectedTheory.confidence)]">{{ selectedTheory.confidence || 'unrated' }}</span>
          <span class="sub-tag">r/{{ selectedTheory.subreddit }}</span>
          <span>↑ {{ selectedTheory.upvotes }}</span>
          <a :href="selectedTheory.url" target="_blank" class="view-link">view on reddit</a>
        </div>
        <div class="modal-summary">
          <div class="summary-header">
            <span class="sidebar-title">AI Summary</span>
            <button class="summarize-btn" @click="getSummary" :disabled="summarizing">
              {{ summarizing ? 'Generating...' : summary ? 'Regenerate' : 'Generate Summary' }}
            </button>
          </div>
          <div v-if="summary" class="summary-text">{{ summary }}</div>
          <div v-else class="summary-empty">Click "Generate Summary" to get an AI summary.</div>
        </div>
        <div class="modal-body">{{ stripHtml(selectedTheory.body) }}</div>
        <div v-if="loadingRecs" class="recs-loading">
          <div class="spinner"></div> Finding similar theories...
        </div>
        <div v-else-if="recommendations.length > 0" class="modal-recs">
          <div class="sidebar-title" style="margin-bottom: 12px;">Similar Theories</div>
          <div v-for="rec in recommendations" :key="rec._id" class="rec-card" @click="openTheory(rec)">
            <div class="rec-title">{{ rec.title }}</div>
            <span :class="['badge', confidenceClass(rec.confidence)]">{{ rec.confidence || 'unrated' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const theories = ref([])
const subreddits = ref([])
const activeSub = ref(null)
const search = ref('')
const sort = ref('hot')
const loading = ref(false)
const loadingRecs = ref(false)
const sorts = ['hot', 'new', 'top']
const clusters = ref([])
const selectedTheory = ref(null)
const summary = ref('')
const summarizing = ref(false)
const recommendations = ref([])
const toast = ref('')
const hasMore = ref(true)
const page = ref(0)
const confidenceFilter = ref('all')
const confidenceFilters = ['all', 'high', 'medium', 'low', 'unrated']
const trending = ref([])
const genSubreddit = ref('')
const generating = ref(false)
const generatedTheory = ref('')

const API = 'http://127.0.0.1:8000'

const filteredTheories = computed(() => {
  if (confidenceFilter.value === 'all') return theories.value
  if (confidenceFilter.value === 'unrated') return theories.value.filter(t => !t.confidence)
  return theories.value.filter(t => t.confidence === confidenceFilter.value)
})

function setConfidenceFilter(c) { confidenceFilter.value = c }
function showToast(msg) { toast.value = msg; setTimeout(() => toast.value = '', 3000) }

async function fetchClusters() {
  const res = await axios.get(`${API}/api/clusters/`)
  clusters.value = res.data
}

async function fetchTrending() {
  const res = await axios.get(`${API}/api/theories/trending`)
  trending.value = res.data
}

async function fetchTheories(reset = true) {
  if (reset) { page.value = 0; theories.value = [] }
  loading.value = true
  const params = { sort: sort.value, limit: 20, skip: page.value * 20 }
  if (activeSub.value) params.subreddit = activeSub.value
  if (search.value) params.search = search.value
  const res = await axios.get(`${API}/api/theories/`, { params })
  if (reset) { theories.value = res.data } else { theories.value = [...theories.value, ...res.data] }
  hasMore.value = res.data.length === 20
  loading.value = false
}

async function loadMore() { page.value++; await fetchTheories(false) }

async function fetchSubreddits() {
  const res = await axios.get(`${API}/api/theories/subreddits`)
  const counts = await axios.get(`${API}/api/theories/subreddit-counts`)
  subreddits.value = res.data.map(name => ({ name, count: counts.data[name] || 0 }))
}

async function addSubreddit() {
  const name = prompt('Enter subreddit name (without r/):')
  if (!name) return
  showToast(`Scraping r/${name}...`)
  await axios.post(`${API}/api/scraper/scrape/${name}`)
  setTimeout(() => { fetchSubreddits(); fetchTheories(); showToast(`r/${name} added!`) }, 4000)
}

async function deleteSubreddit(name) {
  if (!confirm(`Delete all theories from r/${name}?`)) return
  await axios.delete(`${API}/api/scraper/subreddit/${name}`)
  showToast(`r/${name} deleted`)
  fetchSubreddits()
  if (activeSub.value === name) activeSub.value = null
  fetchTheories()
}

async function openTheory(theory) {
  selectedTheory.value = theory
  summary.value = theory.summary || ''
  recommendations.value = []
  loadingRecs.value = true
  const res = await axios.get(`${API}/api/theories/recommend/${theory._id}`)
  recommendations.value = res.data
  loadingRecs.value = false
}

async function getSummary() {
  summarizing.value = true
  const res = await axios.post(`${API}/api/theories/summarize/${selectedTheory.value._id}`)
  summary.value = res.data.summary
  summarizing.value = false
}

function closeModal() { selectedTheory.value = null; summary.value = ''; recommendations.value = [] }
function toggleSub(sub) { activeSub.value = activeSub.value === sub ? null : sub }
function shareTheory(theory) { navigator.clipboard.writeText(theory.url); showToast('Link copied!') }

async function generateTheory() {
  generating.value = true
  generatedTheory.value = ''
  const res = await axios.post(`${API}/api/theories/generate`, { subreddit: genSubreddit.value })
  generatedTheory.value = res.data.theory
  generating.value = false
}

function confidenceClass(c) {
  if (c === 'high') return 'badge-high'
  if (c === 'medium') return 'badge-mid'
  return 'badge-low'
}

function stripHtml(html) {
  if (!html) return ''
  return html
    .replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/&#32;/g, ' ').replace(/&nbsp;/g, ' ')
    .replace(/submitted by \/u\/\S+/gi, '').replace(/\[link\]/gi, '').replace(/\[comments\]/gi, '')
    .replace(/\s+/g, ' ').trim()
}

watch([sort, activeSub, search], () => fetchTheories(true))
onMounted(() => { fetchTheories(); fetchSubreddits(); fetchClusters(); fetchTrending() })
</script>