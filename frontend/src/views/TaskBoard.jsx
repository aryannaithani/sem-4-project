import { useState, useEffect } from 'react';
import { getTasks, completeTask, generateTasks } from '../api';
import { CheckCircle, Circle, RefreshCw, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';

const TaskBoard = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const data = await getTasks();
      setTasks(data?.tasks || []);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      const data = await generateTasks();
      if (data.tasks) setTasks(data.tasks);
      else await fetchTasks();
    } catch (error) {
      console.error('Error generating tasks:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleCompleteTask = async (taskId) => {
    try {
      const data = await completeTask(taskId);
      if (data.updated_tasks) setTasks(data.updated_tasks);
      else await fetchTasks();
    } catch (error) {
      console.error('Error completing task:', error);
    }
  };

  if (loading) return <div className="muted">Loading tasks...</div>;

  let pendingTasks = tasks.filter((t) => t.status === 'pending');
  if (filter !== 'all') pendingTasks = pendingTasks.filter((t) => (t.difficulty || 'beginner') === filter);
  const completedTasks = tasks.filter((t) => t.status === 'completed');

  return (
    <div>
      <header className="mb-6 flex flex-col md:flex-row md:justify-between md:items-end gap-4">
        <div>
          <h1 className="title-xl">Task Board</h1>
          <p className="muted mt-2">Deliver measurable work aligned to your roadmap.</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <div className="panel-soft p-1 flex gap-1">
            {['all', 'beginner', 'intermediate', 'advanced'].map((level) => (
              <button
                key={level}
                onClick={() => setFilter(level)}
                className={clsx('btn !py-1.5 !px-3 !text-xs capitalize', filter === level && 'btn-primary')}
              >
                {level}
              </button>
            ))}
          </div>
          <button onClick={handleGenerate} disabled={generating} className="btn btn-primary">
            {generating ? <RefreshCw className="animate-spin" size={16} /> : <Sparkles size={16} />}
            {generating ? 'Generating...' : 'Generate tasks'}
          </button>
        </div>
      </header>

      <div className="grid md:grid-cols-2 gap-4">
        <section className="panel">
          <div className="p-4 border-b border-[#232328] flex justify-between items-center">
            <h2 className="font-semibold">Pending</h2>
            <span className="chip">{pendingTasks.length}</span>
          </div>
          <div className="p-4 space-y-3 max-h-[68vh] overflow-auto">
            {pendingTasks.length === 0 ? (
              <div className="muted text-sm">No pending tasks for this filter.</div>
            ) : (
              pendingTasks.map((task) => (
                <article key={task.id} className="panel-soft p-4">
                  <div className="flex justify-between items-center mb-3">
                    <span className="chip">{task.skill}</span>
                    <span className="chip capitalize">{task.difficulty || 'beginner'}</span>
                  </div>
                  <h3 className="font-semibold leading-snug">{task.task}</h3>
                  <p className="muted text-sm mt-2">{task.reason}</p>
                  <div className="mt-4 flex items-center justify-between">
                    <button onClick={() => handleCompleteTask(task.id)} className="btn">
                      <Circle size={16} /> Mark complete
                    </button>
                    {task.estimated_hours && <span className="muted text-xs">{task.estimated_hours}h estimate</span>}
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

        <section className="panel">
          <div className="p-4 border-b border-[#232328] flex justify-between items-center">
            <h2 className="font-semibold">Completed</h2>
            <span className="chip">{completedTasks.length}</span>
          </div>
          <div className="p-4 space-y-2 max-h-[68vh] overflow-auto">
            {completedTasks.length === 0 ? (
              <div className="muted text-sm">No completed tasks yet.</div>
            ) : (
              completedTasks.slice().reverse().map((task) => (
                <div key={task.id} className="panel-soft p-3 flex items-start justify-between gap-2">
                  <div>
                    <div className="text-sm">{task.task}</div>
                    <div className="text-xs muted mt-1">{task.skill}</div>
                  </div>
                  <CheckCircle size={16} />
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default TaskBoard;
