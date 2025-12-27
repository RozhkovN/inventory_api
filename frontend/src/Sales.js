import React, { useState, useEffect } from 'react';
import { salesAPI, productsAPI } from './api';
import './Sales.css';

function Sales() {
  const [sales, setSales] = useState([]);
  const [products, setProducts] = useState([]);
  const [filterStatus, setFilterStatus] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [formData, setFormData] = useState({
    client_name: '',
    items: [{ product_id: '', quantity: '', sold_price_per_unit: '', coefficient: '1.0' }],
  });

  useEffect(() => {
    loadSales();
    loadProducts();
  }, []);

  const loadSales = async () => {
    setLoading(true);
    try {
      const response = await salesAPI.getAll(filterStatus);
      setSales(response.data);
    } catch (error) {
      setMessage('Ошибка при загрузке продаж');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadProducts = async () => {
    try {
      const response = await productsAPI.getAll();
      setProducts(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    loadSales();
  }, [filterStatus]);

  const handleAddItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { product_id: '', quantity: '', sold_price_per_unit: '', coefficient: '1.0' }]
    }));
  };

  const handleRemoveItem = (index) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const handleItemChange = (index, field, value) => {
    setFormData(prev => {
      const newItems = [...prev.items];
      newItems[index][field] = value;
      return { ...prev, items: newItems };
    });
  };

  const handleOpenModal = () => {
    setFormData({
      client_name: '',
      items: [{ product_id: '', quantity: '', sold_price_per_unit: '', coefficient: '1.0' }],
    });
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Валидация: проверяем что все количества положительные
      for (let item of formData.items) {
        const qty = parseInt(item.quantity);
        if (!item.product_id) {
          setMessage('❌ Выбери товар');
          setLoading(false);
          return;
        }
        if (!item.quantity || qty <= 0) {
          setMessage('❌ Количество должно быть больше 0');
          setLoading(false);
          return;
        }
        if (!item.sold_price_per_unit || parseFloat(item.sold_price_per_unit) <= 0) {
          setMessage('❌ Цена должна быть больше 0');
          setLoading(false);
          return;
        }
      }

      const payload = {
        client_name: formData.client_name,
        items: formData.items.map(item => ({
          product_id: parseInt(item.product_id),
          quantity: parseInt(item.quantity),
          sold_price_per_unit: parseFloat(item.sold_price_per_unit),
          coefficient: parseFloat(item.coefficient),
        }))
      };

      await salesAPI.create(payload);
      setMessage('✅ Продажа создана');
      handleCloseModal();
      loadSales();
    } catch (error) {
      setMessage('❌ Ошибка: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleChangeStatus = async (id, newStatus) => {
    setLoading(true);
    try {
      await salesAPI.updateStatus(id, { payment_status: newStatus });
      setMessage('✅ Статус обновлён');
      loadSales();
    } catch (error) {
      setMessage('❌ Ошибка: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Отменить продажу и вернуть товары?')) return;
    
    setLoading(true);
    try {
      await salesAPI.delete(id);
      setMessage('✅ Продажа отменена');
      loadSales();
    } catch (error) {
      setMessage('❌ Ошибка: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateTotals = () => {
    let totalSale = 0;
    formData.items.forEach(item => {
      const price = parseFloat(item.sold_price_per_unit) || 0;
      const qty = parseInt(item.quantity) || 0;
      const coef = parseFloat(item.coefficient) || 1;
      totalSale += price * qty * coef;
    });
    return totalSale.toFixed(2);
  };

  return (
    <div className="sales">
      <div className="sales-header">
        <h1>💰 Продажи</h1>
        <button className="btn-primary" onClick={handleOpenModal}>
          + Создать продажу
        </button>
      </div>

      {message && (
        <div className={`alert ${message.includes('✅') ? 'alert-success' : 'alert-error'}`}>
          {message}
        </div>
      )}

      <div className="filter-box">
        <label>Фильтр по статусу:</label>
        <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          <option value="">Все</option>
          <option value="PAID">Оплачено</option>
          <option value="UNPAID">Не оплачено</option>
          <option value="PARTIAL">Частично оплачено</option>
        </select>
      </div>

      {loading ? (
        <p>Загрузка...</p>
      ) : (
        <div className="sales-list">
          {sales.length === 0 ? (
            <p>Продаж не найдено</p>
          ) : (
            sales.map(sale => (
              <div key={sale.id} className="sale-card">
                <div className="sale-header-card">
                  <div>
                    <h3>Клиент: {sale.client_name}</h3>
                    <p className="sale-id">Продажа #{sale.id}</p>
                  </div>
                  <div className="sale-status">
                    <select 
                      value={sale.payment_status}
                      onChange={(e) => handleChangeStatus(sale.id, e.target.value)}
                    >
                      <option value="UNPAID">Не оплачено</option>
                      <option value="PAID">Оплачено</option>
                      <option value="PARTIAL">Частично</option>
                    </select>
                  </div>
                </div>

                <div className="sale-items">
                  <table>
                    <thead>
                      <tr>
                        <th>Товар</th>
                        <th>Кол-во</th>
                        <th>Цена за ед.</th>
                        <th>Коэф.</th>
                        <th>Итого</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sale.items.map((item, idx) => (
                        <tr key={idx}>
                          <td>{item.product_name}</td>
                          <td>{item.quantity}</td>
                          <td>₽{parseFloat(item.sold_price_per_unit).toFixed(2)}</td>
                          <td>{parseFloat(item.coefficient).toFixed(2)}</td>
                          <td>₽{(parseFloat(item.sold_price_per_unit) * item.quantity * parseFloat(item.coefficient)).toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="sale-totals">
                  <div className="total-row">
                    <span>Сумма продажи:</span>
                    <strong>₽{parseFloat(sale.total_sale).toFixed(2)}</strong>
                  </div>
                  <div className="total-row">
                    <span>Себестоимость:</span>
                    <span>₽{parseFloat(sale.total_cost).toFixed(2)}</span>
                  </div>
                  <div className="total-row profit">
                    <span>Прибыль:</span>
                    <strong>₽{parseFloat(sale.margin).toFixed(2)}</strong>
                  </div>
                </div>

                <div className="sale-actions">
                  <button className="btn-delete" onClick={() => handleDelete(sale.id)}>
                    🗑️ Отменить
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {showModal && (
        <div className="modal" onClick={handleCloseModal}>
          <div className="modal-content modal-large" onClick={e => e.stopPropagation()}>
            <h2>Создать новую продажу</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Клиент *</label>
                <input
                  type="text"
                  value={formData.client_name}
                  onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                  required
                />
              </div>

              <h3>Товары</h3>
              {formData.items.map((item, index) => (
                <div key={index} className="item-row">
                  <div className="item-field">
                    <label>Товар *</label>
                    <select
                      value={item.product_id}
                      onChange={(e) => handleItemChange(index, 'product_id', e.target.value)}
                      required
                    >
                      <option value="">Выберите товар</option>
                      {products.map(p => (
                        <option key={p.id} value={p.id}>
                          {p.name} (осталось: {p.quantity})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="item-field">
                    <label>Количество *</label>
                    <input
                      type="number"
                      value={item.quantity}
                      onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                      min="1"
                      step="1"
                      required
                    />
                  </div>

                  <div className="item-field">
                    <label>Цена за ед. *</label>
                    <input
                      type="number"
                      step="0.01"
                      value={item.sold_price_per_unit}
                      onChange={(e) => handleItemChange(index, 'sold_price_per_unit', e.target.value)}
                      required
                    />
                  </div>

                  <div className="item-field">
                    <label>Коэффициент</label>
                    <input
                      type="number"
                      step="0.01"
                      value={item.coefficient}
                      onChange={(e) => handleItemChange(index, 'coefficient', e.target.value)}
                    />
                  </div>

                  {formData.items.length > 1 && (
                    <button
                      type="button"
                      className="btn-remove"
                      onClick={() => handleRemoveItem(index)}
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}

              <button type="button" className="btn-secondary" onClick={handleAddItem}>
                + Добавить ещё товар
              </button>

              <div className="sale-preview">
                <strong>Итоговая сумма: ₽{calculateTotals()}</strong>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Создание...' : 'Создать продажу'}
                </button>
                <button type="button" className="btn-cancel" onClick={handleCloseModal}>
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Sales;
