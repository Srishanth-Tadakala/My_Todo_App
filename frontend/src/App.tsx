import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { Archive, ArrowUpRight, Bell, CalendarDays, Check, ChevronDown, CircleHelp, Clock3, Command, Inbox, LayoutGrid, ListTodo, MoreHorizontal, Plus, Search, Settings2, Sparkles, Target, Timer, X } from 'lucide-react'
import './App.css'

type Todo = { id: number; title: string; project: string; priority: 'Urgent' | 'High' | 'Medium' | 'Low'; status: 'In progress' | 'Todo' | 'Completed'; dueLabel: string; estimate: string }

const starterTodos: Todo[] = [
  { id: 1, title: 'Finalize Q3 product narrative', project: 'Northstar launch', priority: 'Urgent', status: 'In progress', dueLabel: 'Today, 9:30 AM', estimate: '45 min' },
  { id: 2, title: 'Review new onboarding flows', project: 'Product design', priority: 'High', status: 'Todo', dueLabel: 'Today, 11:00 AM', estimate: '30 min' },
  { id: 3, title: 'Send research synthesis to team', project: 'Discovery sprint', priority: 'Medium', status: 'Todo', dueLabel: 'Today, 2:00 PM', estimate: '25 min' },
  { id: 4, title: 'Book flight for Austin offsite', project: 'Personal', priority: 'Low', status: 'Todo', dueLabel: 'Today, 5:30 PM', estimate: '15 min' },
  { id: 5, title: 'Update investor metrics dashboard', project: 'Northstar launch', priority: 'High', status: 'Completed', dueLabel: 'Yesterday', estimate: '1 hr' },
]

const schedule = [
  { time: '09:30', title: 'Product narrative review', type: 'Focus block', color: 'coral' },
  { time: '11:00', title: 'Design critique', type: 'Northstar launch', color: 'blue' },
  { time: '13:00', title: 'Lunch & walk', type: 'Personal', color: 'lime' },
  { time: '14:30', title: 'Team weekly sync', type: 'Team ritual', color: 'violet' },
]

const navItems = [
  { label: 'Overview', icon: LayoutGrid }, { label: 'My tasks', icon: ListTodo, count: '12' }, { label: 'Calendar', icon: CalendarDays }, { label: 'Inbox', icon: Inbox, count: '3' },
]

function App() {
  const [todos, setTodos] = useState(starterTodos)
  const [activeNav, setActiveNav] = useState('Overview')
  const [filter, setFilter] = useState<'All' | 'Today' | 'Upcoming'>('Today')
  const [search, setSearch] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isCommandOpen, setIsCommandOpen] = useState(false)
  const visibleTodos = useMemo(() => todos.filter((todo) => {
    const matchesSearch = todo.title.toLowerCase().includes(search.toLowerCase()) || todo.project.toLowerCase().includes(search.toLowerCase())
    const matchesFilter = filter === 'All' || (filter === 'Today' ? todo.dueLabel.includes('Today') : todo.status !== 'Completed')
    return matchesSearch && matchesFilter
  }), [filter, search, todos])
  const completed = todos.filter((todo) => todo.status === 'Completed').length
  const toggleTodo = (id: number) => setTodos((current) => current.map((todo) => todo.id === id ? { ...todo, status: todo.status === 'Completed' ? 'Todo' : 'Completed' } : todo))
  const addTodo = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const title = String(form.get('title') || '').trim()
    if (!title) return
    setTodos((current) => [{ id: Date.now(), title, project: 'Personal', priority: 'Medium', status: 'Todo', dueLabel: 'Today, 6:00 PM', estimate: '25 min' }, ...current])
    setIsModalOpen(false)
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark"><Sparkles size={16} /></span><span>daymark</span></div>
      <div className="workspace-switcher"><div className="avatar avatar-green">SJ</div><div><strong>Sarah’s workspace</strong><small>Personal command center</small></div><ChevronDown size={15} /></div>
      <nav className="main-nav" aria-label="Main navigation"><span className="nav-label">Workspace</span>{navItems.map(({ label, icon: Icon, count }) => <button key={label} className={`nav-item ${activeNav === label ? 'active' : ''}`} onClick={() => setActiveNav(label)}><Icon size={17} /><span>{label}</span>{count && <em>{count}</em>}</button>)}<span className="nav-label nav-label-spaced">Manage</span><button className="nav-item"><Archive size={17} /><span>Projects</span></button><button className="nav-item"><Target size={17} /><span>Goals</span></button><button className="nav-item"><Timer size={17} /><span>Focus mode</span><span className="live-dot" /></button></nav>
      <div className="sidebar-bottom"><button className="nav-item"><Settings2 size={17} /><span>Settings</span></button><button className="nav-item"><CircleHelp size={17} /><span>Help center</span></button><div className="upgrade"><div className="upgrade-icon"><ArrowUpRight size={15} /></div><strong>Make space for focus</strong><p>Unlock unlimited projects and deep work analytics.</p><button>Explore Pro <ArrowUpRight size={13} /></button></div></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div className="breadcrumbs"><span>Workspace</span><span>/</span><strong>{activeNav}</strong></div><div className="top-actions"><button className="search-trigger" onClick={() => setIsCommandOpen(true)}><Search size={16} /><span>Search anything</span><kbd><Command size={12} /> K</kbd></button><button className="icon-button notification" aria-label="Notifications"><Bell size={18} /><i /></button><div className="avatar avatar-coral">SJ</div></div></header>
      <div className="content-wrap">
        <section className="welcome-row"><div><p className="eyebrow"><span className="status-pulse" /> MONDAY, SEPTEMBER 21, 2026</p><h1>Good morning, Sarah <span>✦</span></h1><p className="intro">A clear mind starts with a clear next step. Here’s what deserves your attention today.</p></div><button className="primary-button" onClick={() => setIsModalOpen(true)}><Plus size={17} /> New task</button></section>
        <section className="metric-grid"><div className="metric-card dark"><div className="metric-top"><span>Today’s pulse</span><span className="metric-icon"><Sparkles size={15} /></span></div><strong>On a roll</strong><p>{completed} of {todos.length} tasks complete</p><div className="progress-track"><span style={{ width: `${(completed / todos.length) * 100}%` }} /></div><small>{Math.round((completed / todos.length) * 100)}% of your day is done</small></div><div className="metric-card"><div className="metric-top"><span>Deep work</span><span className="metric-icon coral-bg"><Clock3 size={15} /></span></div><strong>2h 40m</strong><p>Focused this week</p><div className="mini-bars"><i /><i /><i /><i /><i className="muted" /><i className="muted" /><i className="muted" /></div><small>+18% from last week</small></div><div className="metric-card"><div className="metric-top"><span>Open loops</span><span className="metric-icon blue-bg"><ListTodo size={15} /></span></div><strong>{todos.filter((todo) => todo.status !== 'Completed').length}</strong><p>Tasks need your attention</p><div className="loop-tags"><span className="tag urgent">2 urgent</span><span className="tag">4 this week</span></div><small>Down from 14 last Monday</small></div><div className="metric-card"><div className="metric-top"><span>Weekly streak</span><span className="metric-icon lime-bg"><Target size={15} /></span></div><strong>8 days</strong><p>Consistency is compounding</p><div className="week-dots"><i /><i /><i /><i /><i /><i className="today" /><i className="empty" /></div><small>Keep it going today</small></div></section>
        <div className="dashboard-grid"><section className="tasks-panel"><div className="section-heading"><div><span className="section-kicker">YOUR ATTENTION</span><h2>Today’s focus <span className="count-badge">{visibleTodos.length}</span></h2></div><button className="more-button" aria-label="More options"><MoreHorizontal size={19} /></button></div><div className="task-toolbar"><div className="segmented">{(['Today', 'Upcoming', 'All'] as const).map((item) => <button key={item} className={filter === item ? 'selected' : ''} onClick={() => setFilter(item)}>{item}</button>)}</div><button className="filter-button"><Settings2 size={14} /> Filter</button></div><div className="task-list">{visibleTodos.map((todo) => <article className={`task-row ${todo.status === 'Completed' ? 'is-complete' : ''}`} key={todo.id}><button className={`check-circle ${todo.status === 'Completed' ? 'checked' : ''}`} onClick={() => toggleTodo(todo.id)} aria-label={`Mark ${todo.title} complete`}>{todo.status === 'Completed' && <Check size={13} />}</button><div className="task-main"><div className="task-title-line"><strong>{todo.title}</strong>{todo.priority === 'Urgent' && <span className="priority-mark">URGENT</span>}</div><div className="task-meta"><span>{todo.project}</span><span>•</span><span className={todo.status === 'Completed' ? 'done-text' : ''}>{todo.dueLabel}</span></div></div><span className={`priority-dot ${todo.priority.toLowerCase()}`} title={`${todo.priority} priority`} /><span className="estimate">{todo.estimate}</span><button className="row-more" aria-label="Task options"><MoreHorizontal size={16} /></button></article>)}</div><button className="view-all" onClick={() => setFilter('All')}>View all tasks <ArrowUpRight size={14} /></button></section><aside className="right-column"><section className="schedule-panel"><div className="section-heading"><div><span className="section-kicker">YOUR DAY</span><h2>Schedule <span className="date-chip">Sep 21</span></h2></div><button className="more-button" aria-label="Calendar options"><CalendarDays size={18} /></button></div><div className="schedule-list">{schedule.map((item) => <div className="schedule-row" key={item.time}><time>{item.time}</time><div className={`schedule-line ${item.color}`} /><div><strong>{item.title}</strong><span>{item.type}</span></div></div>)}</div><button className="schedule-footer">Open calendar <ArrowUpRight size={14} /></button></section><section className="quote-panel"><div className="quote-mark">“</div><p>The secret of getting ahead is getting started.</p><span>— Mark Twain</span><div className="quote-footer"><span><Sparkles size={13} /> daily note</span><button aria-label="Next quote"><ArrowUpRight size={14} /></button></div></section></aside></div>
      </div>
    </main>
    {isModalOpen && <div className="modal-backdrop" onMouseDown={() => setIsModalOpen(false)}><form className="task-modal" onSubmit={addTodo} onMouseDown={(event) => event.stopPropagation()}><div className="modal-header"><div><span className="section-kicker">QUICK CAPTURE</span><h2>What’s on your mind?</h2></div><button type="button" className="close-button" onClick={() => setIsModalOpen(false)}><X size={18} /></button></div><label>Task title<input name="title" autoFocus placeholder="e.g. Prepare launch brief" /></label><div className="modal-options"><label>Priority<select defaultValue="MEDIUM"><option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>URGENT</option></select></label><label>Due date<input type="date" defaultValue="2026-09-21" /></label></div><button className="primary-button modal-submit" type="submit"><Plus size={17} /> Add to today</button></form></div>}
    {isCommandOpen && <div className="modal-backdrop" onMouseDown={() => setIsCommandOpen(false)}><div className="command-modal" onMouseDown={(event) => event.stopPropagation()}><div className="command-input"><Search size={19} /><input autoFocus value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search tasks, projects, or people" /><kbd>ESC</kbd></div><div className="command-result"><span className="result-icon"><ListTodo size={15} /></span><div><strong>{search ? `Search for “${search}”` : 'Browse your tasks'}</strong><small>Find anything across your workspace</small></div><ArrowUpRight size={15} /></div></div></div>}
  </div>
}

export default App
