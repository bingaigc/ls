export default function MiniMap({ items, onSelect }) {
  return (
    <div className="rounded bg-white p-3 shadow">
      <h3 className="mb-2 text-sm font-semibold">MiniMap 红句导航</h3>
      <div className="flex flex-wrap gap-1">
        {items.map((item) => {
          const cls = item.level === 'heavy' ? 'bg-red-500' : item.level === 'medium' ? 'bg-orange-500' : 'bg-emerald-500'
          return (
            <button
              key={item.id}
              onClick={() => onSelect(item.id)}
              className={`h-5 w-5 rounded-sm ${cls}`}
              title={`#${item.id} ${item.level}`}
            />
          )
        })}
      </div>
    </div>
  )
}
