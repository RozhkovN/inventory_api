import React, { useState, useEffect } from 'react';
import { historyAPI, productsAPI } from './api';
import './History.css';

function History() {
  const [history, setHistory] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [filters, setFilters] = useState({
    product_id: '',
    operation_type: '',
    days: '',
  });

  useEffect(() => {
    loadHistory();
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await productsAPI.getAll();
      setProducts(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const loadHistory = async (appliedFilters = filters) => {
    setLoading(true);
    try {
      const params = {};
      if (appliedFilters.product_id) params.product_id = appliedFilters.product_id;
      if (appliedFilters.operation_type) params.operation_type = appliedFilters.operation_type;
      if (appliedFilters.days) params.days = appliedFilters.days;

      const response = await historyAPI.getHistory(params);
      setHistory(response.data);
    } catch (error) {
      setMessage('Ошибка при загрузке истории');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
  };

  const handleApplyFilters = () => {
    loadHistory(filters);
  };

  const handleClearFilters = () => {
    const cleared = { product_id: '', operation_type: '', days: '' };
    setFilters(cleared);
    loadHistory(cleared);
  };

  const getOperationTypeLabel = (type) => {
    const labels = {
      'INCOMING': '📥 Приход',
      'SALE': '💸 Продажа',
      'ADJUSTMENT': '🔧 Корректировка',
    };
    return labels[type] || type;
  };

  const getOperationColor = (type) => {
    const colors = {
      'INCOMING': '#4CAF50',
      'SALE': '#f44336',
      'ADJUSTMENT': '#2196F3',
    };
    return colors[type] || '#999';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="history">
      <h1>📊 История операций</h1>

      {message && (
        <div className={`alert ${message.includes('✅') ? 'alert-success' : 'alert-error'}`}>
          {message}
        </div>
      )}

      <div className="filters-panel">
        <div className="filter-group">
          <label>Товар:</label>
          <select
            value={filters.product_id}
            onChange={(e) => handleFilterChange('product_id', e.target.value)}
          >
            <option value="">Все товары</option>
            {products.map(p => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Тип операции:</label>
          <select
            value={filters.operation_type}
            onChange={(e) => handleFilterChange('operation_type', e.target.value)}
          >
            <option value="">Все типы</option>
            <option value="INCOMING">Приход</option>
            <option value="SALE">Продажа</option>
            <option value="ADJUSTMENT">Корректировка</option>
          </select>
        </div>

        <div className="filter-group">
          <label>За последние дни:</label>
          <input
            type="number"
            value={filters.days}
            onChange={(e) => handleFilterChange('days', e.target.value)}
            placeholder="Все дни"
            min="1"
          />
        </div>

        <button className="btn-primary" onClick={handleApplyFilters}>
          Применить
        </button>
        <button className="btn-secondary" onClick={handleClearFilters}>
          Очистить
        </button>
      </div>

      {loading ? (
        <p>Загрузка...</p>
      ) : (
        <div className="history-list">
          {history.length === 0 ? (
            <p>История не найдена</p>
          ) : (
            history.map((record, idx) => (
              <div key={idx} className="history-item">
                <div 
                  className="operation-badge"
                  style={{ backgroundColor: getOperationColor(record.operation_type) }}
                >
                  {getOperationTypeLabel(record.operation_type)}
                </div>

                <div className="history-content">
                  <h4>{record.product_name}</h4>
                  <p className="timestamp">
                    🕐 {formatDate(record.timestamp)}
                  </p>

                  <div className="operation-details">
                    <div className="detail-row">
                      <span>Изменение количества:</span>
                      <strong className={record.quantity_change >= 0 ? 'positive' : 'negative'}>
                        {record.quantity_change >= 0 ? '+' : ''}{record.quantity_change}
                      </strong>
                    </div>

                    {record.old_quantity !== null && record.new_quantity !== null && (
                      <div className="detail-row">
                        <span>Было → Стало:</span>
                        <span>{record.old_quantity} → {record.new_quantity}</span>
                      </div>
                    )}

                    {record.old_purchase_price && record.new_purchase_price && (
                      <div className="detail-row">
                        <span>Цена закупки:</span>
                        <span>₽{parseFloat(record.old_purchase_price).toFixed(2)} → ₽{parseFloat(record.new_purchase_price).toFixed(2)}</span>
                      </div>
                    )}

                    {record.old_coefficient && record.new_coefficient && (
                      <div className="detail-row">
                        <span>Коэффициент:</span>
                        <span>{parseFloat(record.old_coefficient).toFixed(2)} → {parseFloat(record.new_coefficient).toFixed(2)}</span>
                      </div>
                    )}

                    {record.sold_price_per_unit && (
                      <div className="detail-row">
                        <span>Цена продажи:</span>
                        <span>₽{parseFloat(record.sold_price_per_unit).toFixed(2)}</span>
                      </div>
                    )}

                    {record.reason && (
                      <div className="detail-row">
                        <span>Причина:</span>
                        <em>{record.reason}</em>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default History;
