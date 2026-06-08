import React, { useEffect, useState } from 'react';
import { apiGet, apiPost } from '../utils/apiClient';
import { Alert, EmptyState, Spinner } from './ui';

function Reviews({ hospital }) {
  const [items, setItems] = useState([]);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const load = async () => {
    try {
      const data = await apiGet(`/api/reviews?hospital_id=${hospital.id}`);
      setItems(Array.isArray(data) ? data : []);
      setError(null);
    } catch (e) {
      setError(e.message || 'Failed to load reviews');
      setItems([]);
    }
  };

  useEffect(() => {
    if (hospital?.id) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hospital?.id]);

  const submit = async (e) => {
    e.preventDefault();
    
    if (!comment.trim()) {
      setError('Please add a comment');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);
    
    try {
      await apiPost('/api/reviews', {
        hospital_id: hospital.id,
        hospital_name: hospital.name,
        hospital_address: hospital.address,
        latitude: hospital.latitude,
        longitude: hospital.longitude,
        rating: parseInt(rating, 10),
        comment: comment.trim(),
      });

      setSuccess(true);
      setComment('');
      setRating(5);
      setTimeout(() => setSuccess(false), 3000);
      await load();
    } catch (e) {
      setError(e.message || 'Failed to add review');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reviews">
      <h4>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" strokeWidth="1"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        Reviews
      </h4>
      {items.length === 0 && (
        <EmptyState title="No reviews yet" description="Be the first to share your experience." />
      )}
      {items.slice(0, 3).map(r => (
        <div key={r.id} className="review-item">
          <strong>{Array.from({length: r.rating}).map((_, i) => <svg key={i} width="14" height="14" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" strokeWidth="1" style={{marginRight:1}}><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>)}</strong> — {r.comment}
          <div className="review-meta">by {r.username || 'User'} on {new Date(r.created_at).toLocaleDateString()}</div>
        </div>
      ))}
      <form onSubmit={submit} className="review-form">
        <Alert type="error">{error}</Alert>
        {success && <Alert type="success">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>
          Review added successfully!
        </Alert>}
        <label>
          Rating
          <select value={rating} onChange={e => setRating(e.target.value)}>
            {[1,2,3,4,5].map(n => <option key={n} value={n}>{n} Star{n > 1 ? 's' : ''}</option>)}
          </select>
        </label>
        <label>
          Comment
          <textarea 
            value={comment} 
            onChange={e => setComment(e.target.value)} 
            placeholder="Share your experience..." 
            rows="3"
            required
          />
        </label>
        <button className="btn-small" type="submit" disabled={loading}>
          {loading ? <Spinner label="Submitting..." inline /> : 'Add Review'}
        </button>
      </form>
    </div>
  );
}

export default Reviews;
