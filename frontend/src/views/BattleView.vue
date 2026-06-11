<template>
  <div class="battle-page">
    <header class="header">
      <div class="logo" @click="$router.push('/')" style="cursor:pointer">
        <div class="logo-icon">FL</div>
        <div>
          <div class="logo-text">FanLens</div>
          <div class="logo-sub">Theory Intelligence</div>
        </div>
      </div>
      <div class="battle-header-title">⚔️ Theory Battle</div>
    </header>

    <div class="battle-container">
      <div class="battle-pick">
        <div class="pick-card" :class="{ selected: theory1 }" @click="pickMode = 1">
          <div v-if="!theory1" class="pick-placeholder">
            <span class="pick-icon">+</span>
            <span>Pick Theory 1</span>
          </div>
          <div v-else class="picked-theory">
            <span :class="['badge', confidenceClass(theory1.confidence)]">{{ theory1.confidence || 'unrated' }}</span>
            <div class="picked-title">{{ theory1.title }}</div>
            <div class="picked-sub">r/{{ theory1.subreddit }}</div>
          </div>
        </div>

        <div class="vs-badge">VS</div>

        <div class="pick-card" :class="{ selected: theory2 }" @click="pickMode = 2">
          <div v-if="!theory2" class="pick-placeholder">
            <span class="pick-icon">+</span>
            <span>Pick Theory 2</span>
          </div>
          <div v-else class="picked-theory">
            <span :class="['badge', confidenceClass(theory2.confidence)]">{{ theory2.confidence || 'unrated' }}</span>
            <div class="picked-title">{{ theory2.title }}</div>
            <div class="picked-sub">r/{{ theory2.subreddit }}</div>
          </div>
        </div>
      </div>

      <button v-if="theory1 && theory2" class="battle-btn" @click="runBattle" :disabled="battling">
        {{ battling ? 'AI is judging...' : '⚔️ Battle!' }}
      </button>

      <!-- Result -->
      <div v-if="result" class="battle-result">
        <div class="winner-banner">
          🏆 Winner: {{ result.winner === 'theory1' ? theory1.title : theory2.title }}
        </div>
        <div class="verdict">{{ result.verdict }}</div>
        <div class="scores">
          <div class="score-card" :class="{ winner: result.winner === 'theory1' }">
            <div class="score-title">{{ theory1.title }}</div>
            <div class="score-num">{{ result.theory1_score }}/10</div>
            <div class="score-strength">💪 {{ result.theory1_strength }}</div>
          </div>
          <div class="score-card" :class="{ winner: result.winner === 'theory2' }">
            <div class="score-title">{{ theory2.title }}</div>
            <div class="score-num">{{ result.theory2_score }}/10</div>
            <div class="score-strength">💪 {{ result.theory2_strength }}</div>
          </div>
        </div>
        <button class="reset-btn" @click="resetBattle">Try Again</button>
      </div>

      <!-- Theory picker -->
      <div v-if="pickMode" class="theory-picker">
        <div class="picker-header">
          <span>Select Theory {{ pickMode }}</span>
          <button @click="pickMode = null">✕</button>
        </div>
        <input v-model="pickerSearch" placeholder="Search theories..." class="picker-search" />
        <div class="picker-list">
          <div
            v-for="t in filteredPicker"
            :key="t._id"
            class="picker-item"
            @click="selectTheory(t)"
          >
            <div class="picker-title">{{ t.title }}</div>
            <span class="sub-tag">r/{{ t.subreddit }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://127.0.0.1:8000'
const theory1 = ref(null)
const theory2 = ref(null)
const battling = ref(false)
const result = ref(null)
const pickMode = ref(null)
const pickerSearch = ref('')
const allTheories = ref([])

const filteredPicker = computed(() => {
  if (!pickerSearch.value) return allTheories.value.slice(0, 20)
  return allTheories.value.filter(t =>
    t.title.toLowerCase().includes(pickerSearch.value.toLowerCase())
  ).slice(0, 20)
})

async function loadTheories() {
  const res = await axios.get(`${API}/api/theories/?limit=100`)
  allTheories.value = res.data
}

function selectTheory(t) {
  if (pickMode.value === 1) theory1.value = t
  else theory2.value = t
  pickMode.value = null
  pickerSearch.value = ''
}

async function runBattle() {
  battling.value = true
  result.value = null
  const res = await axios.post(`${API}/api/theories/battle`, {
    theory1_id: theory1.value._id,
    theory2_id: theory2.value._id
  })
  result.value = res.data
  battling.value = false
}

function resetBattle() {
  theory1.value = null
  theory2.value = null
  result.value = null
}

function confidenceClass(c) {
  if (c === 'high') return 'badge-high'
  if (c === 'medium') return 'badge-mid'
  return 'badge-low'
}

onMounted(loadTheories)
</script>