import { useMemo, useState } from 'react'
import { architectureMeta, nodes, relationships } from './data.js'

const statusOrder = [
  'ALL',
  'WORKBENCH',
  'STAGING',
  'NURSERY',
  'CRIB',
  'CONCEPT',
  'FROZEN',
  'UNVERIFIED',
]

const normalize = (value) => String(value ?? '').toLowerCase()

function App() {
  const nodeById = useMemo(() => new Map(nodes.map((node) => [node.id, node])), [])
  const childrenByParent = useMemo(() => {
    const map = new Map()
    nodes.forEach((node) => {
      const key = node.parentId ?? '__root__'
      if (!map.has(key)) map.set(key, [])
      map.get(key).push(node)
    })
    for (const list of map.values()) {
      list.sort((a, b) => a.name.localeCompare(b.name))
    }
    return map
  }, [])

  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('ALL')
  const [selectedId, setSelectedId] = useState('blueprint-explorer')
  const [collapsed, setCollapsed] = useState(new Set(['product-suite']))
  const [mobileDetailsOpen, setMobileDetailsOpen] = useState(false)

  const selected = nodeById.get(selectedId) ?? nodes[0]

  const matchesNode = (node) => {
    const statusMatch = status === 'ALL' || node.status === status
    if (!statusMatch) return false
    if (!query.trim()) return true

    const searchable = [
      node.name,
      node.shortDescription,
      node.description,
      node.nodeType,
      node.status,
      node.evidenceState,
      node.owner,
      node.decisionState,
      ...node.capabilities,
      ...node.repositories,
      ...node.environments,
      ...node.agents,
      ...node.workflows,
      ...node.sourceReferences,
    ]
      .map(normalize)
      .join(' ')

    return searchable.includes(normalize(query.trim()))
  }

  const { includedIds, directMatchIds } = useMemo(() => {
    const direct = new Set(nodes.filter(matchesNode).map((node) => node.id))
    const included = new Set(direct)

    for (const id of direct) {
      let current = nodeById.get(id)
      while (current?.parentId) {
        included.add(current.parentId)
        current = nodeById.get(current.parentId)
      }
    }

    return { includedIds: included, directMatchIds: direct }
  }, [query, status, nodeById])

  const visibleByDepth = useMemo(() => {
    const levels = []
    const searching = Boolean(query.trim()) || status !== 'ALL'

    const visit = (node, depth, ancestorHidden) => {
      if (!includedIds.has(node.id)) return
      if (!levels[depth]) levels[depth] = []
      levels[depth].push({
        ...node,
        contextOnly: !directMatchIds.has(node.id),
      })

      const isCollapsed = !searching && collapsed.has(node.id)
      if (ancestorHidden || isCollapsed) return

      const children = childrenByParent.get(node.id) ?? []
      children.forEach((child) => visit(child, depth + 1, false))
    }

    ;(childrenByParent.get('__root__') ?? []).forEach((root) => visit(root, 0, false))
    return levels.filter(Boolean)
  }, [childrenByParent, collapsed, directMatchIds, includedIds, query, status])

  const downstream = useMemo(
    () => nodes.filter((node) => node.dependencies.includes(selected.id)),
    [selected.id],
  )

  const dependencies = selected.dependencies
    .map((id) => nodeById.get(id))
    .filter(Boolean)

  const children = childrenByParent.get(selected.id) ?? []
  const parent = selected.parentId ? nodeById.get(selected.parentId) : null

  const toggleCollapsed = (id) => {
    setCollapsed((current) => {
      const next = new Set(current)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const selectNode = (id) => {
    setSelectedId(id)
    setMobileDetailsOpen(true)
  }

  const resetView = () => {
    setQuery('')
    setStatus('ALL')
    setCollapsed(new Set(['product-suite']))
  }

  const exportArchitecture = () => {
    const payload = {
      meta: architectureMeta,
      exportedAt: new Date().toISOString(),
      nodes,
      relationships,
    }
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `conrad-blueprint-${architectureMeta.version}.json`
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
  }

  const statusCounts = useMemo(
    () =>
      nodes.reduce(
        (acc, node) => {
          acc[node.status] = (acc[node.status] ?? 0) + 1
          return acc
        },
        { ALL: nodes.length },
      ),
    [],
  )

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <div className="eyebrow">BLUE COLLAR APPS OS / COMPANY CONTROL</div>
          <h1>CONRAD BLUEPRINT EXPLORER</h1>
          <p className="subtitle">
            Governed architecture map. Conrad uses the map; Conrad is not the map.
          </p>
        </div>
        <div className="topbar-actions">
          <span className="build-tag">V1 · WORKBENCH</span>
          <button className="button button-secondary" type="button" onClick={exportArchitecture}>
            EXPORT JSON
          </button>
        </div>
      </header>

      <section className="governance-strip" aria-label="Governance notice">
        <span>AS OF {architectureMeta.asOf}</span>
        <span>{architectureMeta.decisionNotice}</span>
        <span>UNKNOWN DATA IS LABELED — NEVER GUESSED</span>
      </section>

      <main className="workspace">
        <section className="explorer-panel">
          <div className="control-rail">
            <label className="search-field">
              <span>SEARCH THE SYSTEM</span>
              <input
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                aria-label="Search product, agent, service, owner, or capability"
              />
            </label>
            <button className="button button-ghost" type="button" onClick={resetView}>
              RESET VIEW
            </button>
          </div>

          <div className="filters" aria-label="Status filters">
            {statusOrder.map((item) => (
              <button
                key={item}
                className={`filter-chip ${status === item ? 'active' : ''}`}
                type="button"
                onClick={() => setStatus(item)}
              >
                <span>{item}</span>
                <strong>{statusCounts[item] ?? 0}</strong>
              </button>
            ))}
          </div>

          <div className="map-summary">
            <span>{directMatchIds.size} direct matches</span>
            <span>{visibleByDepth.length} visible levels</span>
            <span>{relationships.length} recorded dependencies</span>
          </div>

          <div className="level-map" aria-label="Architecture hierarchy">
            {visibleByDepth.length === 0 ? (
              <div className="empty-state">
                <strong>NO MATCHING SYSTEMS</strong>
                <span>Change the search or status filter.</span>
              </div>
            ) : (
              visibleByDepth.map((level, depth) => (
                <section className="level-column" key={`level-${depth}`}>
                  <div className="level-label">LEVEL {depth + 1}</div>
                  <div className="level-stack">
                    {level.map((node) => {
                      const childCount = (childrenByParent.get(node.id) ?? []).length
                      const isSelected = selected.id === node.id
                      const isCollapsed = collapsed.has(node.id)
                      return (
                        <article
                          key={node.id}
                          className={`node-card ${isSelected ? 'selected' : ''} ${
                            node.contextOnly ? 'context-only' : ''
                          }`}
                        >
                          <button
                            type="button"
                            className="node-main"
                            onClick={() => selectNode(node.id)}
                            aria-pressed={isSelected}
                          >
                            <span className="node-topline">
                              <span className={`status-dot status-${node.status.toLowerCase()}`} />
                              <span className="node-type">{node.nodeType}</span>
                              <span className={`evidence evidence-${node.evidenceState.toLowerCase()}`}>
                                {node.evidenceState}
                              </span>
                            </span>
                            <strong>{node.name}</strong>
                            <span>{node.shortDescription}</span>
                          </button>
                          {childCount > 0 && (
                            <button
                              type="button"
                              className="collapse-button"
                              onClick={() => toggleCollapsed(node.id)}
                              aria-label={`${isCollapsed ? 'Expand' : 'Collapse'} ${node.name}`}
                            >
                              {isCollapsed ? '+' : '−'} {childCount}
                            </button>
                          )}
                        </article>
                      )
                    })}
                  </div>
                </section>
              ))
            )}
          </div>
        </section>

        <aside className={`detail-panel ${mobileDetailsOpen ? 'mobile-open' : ''}`}>
          <button
            type="button"
            className="detail-close"
            onClick={() => setMobileDetailsOpen(false)}
            aria-label="Close details"
          >
            CLOSE
          </button>
          <div className="detail-kicker">SELECTED NODE</div>
          <div className="detail-heading">
            <div>
              <h2>{selected.name}</h2>
              <p>{selected.shortDescription}</p>
            </div>
            <span className={`status-badge status-${selected.status.toLowerCase()}`}>
              {selected.status}
            </span>
          </div>

          <div className="detail-grid">
            <Metric label="TYPE" value={selected.nodeType} />
            <Metric label="EVIDENCE" value={selected.evidenceState} />
            <Metric label="RISK" value={selected.riskLevel} />
            <Metric label="DECISION" value={selected.decisionState} />
          </div>

          <DetailSection title="PURPOSE">
            <p>{selected.description}</p>
          </DetailSection>

          <DetailSection title="OWNERSHIP & VERIFICATION">
            <Definition label="Owner" value={selected.owner} />
            <Definition label="Last verified" value={selected.lastVerifiedAt ?? 'UNKNOWN'} />
            <Definition label="Verified by" value={selected.verifiedBy ?? 'UNKNOWN'} />
          </DetailSection>

          <DetailSection title="RELATIONSHIPS">
            <Relation label="Parent" nodes={parent ? [parent] : []} onSelect={selectNode} />
            <Relation label="Children" nodes={children} onSelect={selectNode} />
            <Relation label="Depends on" nodes={dependencies} onSelect={selectNode} />
            <Relation label="Used by" nodes={downstream} onSelect={selectNode} />
          </DetailSection>

          <ListSection title="CAPABILITIES" items={selected.capabilities} />
          <ListSection title="REPOSITORIES" items={selected.repositories} mono />
          <ListSection title="ENVIRONMENTS" items={selected.environments} />
          <ListSection title="AGENTS" items={selected.agents} />
          <ListSection title="WORKFLOWS" items={selected.workflows} />
          <ListSection title="SOURCE REFERENCES" items={selected.sourceReferences} mono />
        </aside>
      </main>

      <footer className="footer">
        <span>BCA TRENCH DESIGN · ORANGE IS HEAT, NOT PAINT</span>
        <span>READ-ONLY V1 · NO SECRETS · NO PRICING CLAIMS</span>
      </footer>
    </div>
  )
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function DetailSection({ title, children }) {
  return (
    <section className="detail-section">
      <h3>{title}</h3>
      {children}
    </section>
  )
}

function Definition({ label, value }) {
  return (
    <div className="definition-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function Relation({ label, nodes: relationNodes, onSelect }) {
  return (
    <div className="relation-row">
      <span>{label}</span>
      <div>
        {relationNodes.length === 0 ? (
          <em>None recorded</em>
        ) : (
          relationNodes.map((node) => (
            <button type="button" key={node.id} onClick={() => onSelect(node.id)}>
              {node.name}
            </button>
          ))
        )}
      </div>
    </div>
  )
}

function ListSection({ title, items, mono = false }) {
  if (!items.length) return null
  return (
    <DetailSection title={title}>
      <ul className={mono ? 'mono-list' : ''}>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </DetailSection>
  )
}

export default App
