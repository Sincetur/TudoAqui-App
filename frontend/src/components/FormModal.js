import React from 'react';
import { X } from 'lucide-react';

export default function FormModal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="form-modal">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-dark-900 border border-dark-800 rounded-2xl w-full max-w-lg max-h-[85vh] overflow-y-auto animate-slide-up">
        <div className="sticky top-0 bg-dark-900 border-b border-dark-800 px-5 py-3 flex items-center justify-between z-10 rounded-t-2xl">
          <h2 className="text-white font-semibold text-base">{title}</h2>
          <button onClick={onClose} className="p-1.5 rounded-lg text-dark-400 hover:text-white hover:bg-dark-800 transition" data-testid="modal-close-btn">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}

export function FormField({ label, children, error }) {
  return (
    <div className="mb-4">
      <label className="block text-dark-300 text-xs font-medium mb-1.5">{label}</label>
      {children}
      {error && <p className="text-red-400 text-xs mt-1">{error}</p>}
    </div>
  );
}

export function FormInput({ name, type = 'text', placeholder, required, defaultValue, ...props }) {
  return (
    <input
      name={name}
      type={type}
      placeholder={placeholder}
      required={required}
      defaultValue={defaultValue}
      data-testid={`form-field-${name}`}
      className="w-full px-3 py-2.5 bg-dark-800 border border-dark-700 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition"
      {...props}
    />
  );
}

export function FormTextarea({ name, placeholder, rows = 3, ...props }) {
  return (
    <textarea
      name={name}
      placeholder={placeholder}
      rows={rows}
      data-testid={`form-field-${name}`}
      className="w-full px-3 py-2.5 bg-dark-800 border border-dark-700 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition resize-none"
      {...props}
    />
  );
}

export function FormSelect({ name, options, placeholder, ...props }) {
  return (
    <select
      name={name}
      data-testid={`form-field-${name}`}
      className="w-full px-3 py-2.5 bg-dark-800 border border-dark-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary-500 transition"
      {...props}
    >
      {placeholder && <option value="">{placeholder}</option>}
      {options.map(o => (
        <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  );
}

export function SubmitButton({ loading, children }) {
  return (
    <button
      type="submit"
      disabled={loading}
      data-testid="form-submit-btn"
      className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg text-sm transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
    >
      {loading ? (
        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
      ) : children}
    </button>
  );
}
