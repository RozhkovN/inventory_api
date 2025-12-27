import React, { useState, useEffect } from 'react';
import { productsAPI } from './api';
import './Warehouse.css';

function Warehouse() {
  const [products, setProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    purchase_price: '',
    coefficient: '1.0',
    quantity: '',
  });

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const response = await productsAPI.getAll();
      setProducts(response.data);
    } catch (error) {
      setMessage('Ошибка при загрузке товаров');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    setSearchQuery(e.target.value);
    if (e.target.value) {
      try {
        const response = await productsAPI.search(e.target.value);
        setProducts(response.data);
      } catch (error) {
        console.error(error);
      }
    } else {
      loadProducts();
    }
  };

  const handleOpenModal = (product = null) => {
    if (product) {
      setEditingId(product.id);
      setFormData({
        name: product.name,
        sku: product.sku || '',
        purchase_price: product.purchase_price,
        coefficient: product.coefficient,
        quantity: product.quantity,
      });
    } else {
      setEditingId(null);
      setFormData({
        name: '',
        sku: '',
        purchase_price: '',
        coefficient: '1.0',
        quantity: '',
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...formData,
        purchase_price: parseFloat(formData.purchase_price),
        coefficient: parseFloat(formData.coefficient),
        quantity: parseInt(formData.quantity),
      };

      if (editingId) {
        await productsAPI.update(editingId, payload);
        setMessage('✅ Товар обновлён');
      } else {
        await productsAPI.create(payload);
        setMessage('✅ Товар добавлен');
      }

      handleCloseModal();
      loadProducts();
    } catch (error) {
      setMessage('❌ Ошибка: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить товар?')) return;
    
    setLoading(true);
    try {
      await productsAPI.delete(id);
      setMessage('✅ Товар удалён');
      loadProducts();
    } catch (error) {
      setMessage('❌ Ошибка: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="warehouse">
      <div className="warehouse-header">
        <h1>📦 Склад</h1>
        <button className="btn-primary" onClick={() => handleOpenModal()}>
          + Добавить товар
        </button>
      </div>

      {message && (
        <div className={`alert ${message.includes('✅') ? 'alert-success' : 'alert-error'}`}>
          {message}
        </div>
      )}

      <div className="search-box">
        <input
          type="text"
          placeholder="Поиск по названию товара..."
          value={searchQuery}
          onChange={handleSearch}
        />
      </div>

      {loading ? (
        <p>Загрузка...</p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Название</th>
                <th>SKU</th>
                <th>Цена закупки</th>
                <th>Коэффициент</th>
                <th>Итоговая цена</th>
                <th>Количество</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {products.length === 0 ? (
                <tr><td colSpan="7" style={{ textAlign: 'center' }}>Товаров не найдено</td></tr>
              ) : (
                products.map(product => (
                  <tr key={product.id}>
                    <td>{product.name}</td>
                    <td>{product.sku || '-'}</td>
                    <td>₽{parseFloat(product.purchase_price).toFixed(2)}</td>
                    <td>{parseFloat(product.coefficient).toFixed(2)}</td>
                    <td><strong>₽{parseFloat(product.final_price).toFixed(2)}</strong></td>
                    <td><span className="quantity-badge">{product.quantity}</span></td>
                    <td className="actions">
                      <button className="btn-edit" onClick={() => handleOpenModal(product)}>
                        ✏️
                      </button>
                      <button className="btn-delete" onClick={() => handleDelete(product.id)}>
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal" onClick={handleCloseModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h2>{editingId ? 'Редактировать товар' : 'Добавить новый товар'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Название *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>SKU</label>
                <input
                  type="text"
                  name="sku"
                  value={formData.sku}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Цена закупки *</label>
                <input
                  type="number"
                  step="0.01"
                  name="purchase_price"
                  value={formData.purchase_price}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Коэффициент (НДС, скидка и т.д.)</label>
                <input
                  type="number"
                  step="0.01"
                  name="coefficient"
                  value={formData.coefficient}
                  onChange={handleChange}
                />
                <small>По дефолту: 1.0 (скидка 0.9, НДС 1.18)</small>
              </div>

              <div className="form-group">
                <label>Количество *</label>
                <input
                  type="number"
                  name="quantity"
                  value={formData.quantity}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Сохранение...' : 'Сохранить'}
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

export default Warehouse;
