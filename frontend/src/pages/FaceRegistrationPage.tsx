import React, { useState, useCallback, useRef } from 'react';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import {
  Users,
  UserPlus,
  Trash2,
  Upload,
  CheckCircle,
  XCircle,
  Camera,
  Brain,
} from 'lucide-react';

interface Person {
  id: string;
  name: string;
  image_count: number;
  encoding_count: number;
  thumbnail_b64: string | null;
}

interface FaceStatus {
  is_trained: boolean;
  person_count: number;
  total_encodings: number;
}

interface ImagePreview {
  file: File;
  url: string;
  status: 'pending' | 'ok' | 'error';
  message?: string;
}

export default function FaceRegistrationPage() {
  const {
    data: persons,
    loading: personsLoading,
    refetch: refetchPersons,
  } = useApi<Person[]>(api.getFaces as () => Promise<Person[]>);

  const { data: faceStatus, refetch: refetchStatus } = useApi<FaceStatus>(
    api.getFaceStatus as () => Promise<FaceStatus>
  );

  const [showAddForm, setShowAddForm] = useState(false);
  const [personName, setPersonName] = useState('');
  const [imagePreviews, setImagePreviews] = useState<ImagePreview[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);

  const handleFiles = useCallback((files: FileList | File[]) => {
    const arr = Array.from(files).filter((f) =>
      f.type.startsWith('image/')
    );
    const previews: ImagePreview[] = arr.map((file) => ({
      file,
      url: URL.createObjectURL(file),
      status: 'pending',
    }));
    setImagePreviews((prev) => [...prev, ...previews]);
    setUploadError(null);
    setUploadSuccess(null);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [handleFiles]
  );

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const removePreview = (index: number) => {
    setImagePreviews((prev) => {
      const updated = [...prev];
      URL.revokeObjectURL(updated[index].url);
      updated.splice(index, 1);
      return updated;
    });
  };

  const resetForm = () => {
    setPersonName('');
    imagePreviews.forEach((p) => URL.revokeObjectURL(p.url));
    setImagePreviews([]);
    setUploadError(null);
    setUploadSuccess(null);
    setShowAddForm(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!personName.trim()) {
      setUploadError('Please enter a name.');
      return;
    }
    if (imagePreviews.length === 0) {
      setUploadError('Please select at least one image.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const result = await api.addPerson(
        personName.trim(),
        imagePreviews.map((p) => p.file)
      );

      // Mark previews based on errors list
      const errorMessages: string[] = result.errors || [];
      setImagePreviews((prev) =>
        prev.map((p, i) => {
          const err = errorMessages.find((e: string) => e.startsWith(`Image ${i + 1}:`));
          return { ...p, status: err ? 'error' : 'ok', message: err };
        })
      );

      setUploadSuccess(
        `✓ ${result.name} registered with ${result.encodings_added} face encoding(s).`
      );
      refetchPersons();
      refetchStatus();

      // Auto-close after 2s
      setTimeout(() => {
        resetForm();
      }, 2000);
    } catch (err: any) {
      setUploadError(err.message || 'Failed to add person.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (personId: string) => {
    if (!confirm('Delete this person from the face recognition database?')) return;
    setDeletingId(personId);
    try {
      await api.deletePerson(personId);
      refetchPersons();
      refetchStatus();
    } catch {
      // ignore
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Users className="w-7 h-7 text-violet-600" />
            Face Registration
          </h1>
          <p className="text-slate-500 mt-1 text-sm">
            Register known individuals for real-time face recognition in the detection feed.
          </p>
        </div>
        <button
          onClick={() => setShowAddForm((v) => !v)}
          className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors text-sm font-medium shadow-sm"
        >
          <UserPlus className="w-4 h-4" />
          Add Person
        </button>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-violet-100 flex items-center justify-center">
            <Brain className="w-5 h-5 text-violet-600" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Model Status</p>
            <p
              className={`text-sm font-bold ${
                faceStatus?.is_trained ? 'text-emerald-600' : 'text-amber-500'
              }`}
            >
              {faceStatus?.is_trained ? '✓ Trained' : '○ Not Trained'}
            </p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
            <Users className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Registered Persons</p>
            <p className="text-sm font-bold text-slate-900">
              {faceStatus?.person_count ?? 0}
            </p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-cyan-100 flex items-center justify-center">
            <Camera className="w-5 h-5 text-cyan-600" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Total Encodings</p>
            <p className="text-sm font-bold text-slate-900">
              {faceStatus?.total_encodings ?? 0}
            </p>
          </div>
        </div>
      </div>

      {/* Add Person Form */}
      {showAddForm && (
        <div className="bg-white rounded-xl border border-violet-200 shadow-sm overflow-hidden">
          <div className="bg-violet-50 px-5 py-4 border-b border-violet-100 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-violet-900 flex items-center gap-2">
              <UserPlus className="w-4 h-4" />
              Register New Person
            </h2>
            <button
              onClick={resetForm}
              className="text-slate-400 hover:text-slate-600 text-lg leading-none"
            >
              ×
            </button>
          </div>
          <form onSubmit={handleSubmit} className="p-5 space-y-5">
            {/* Name field */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Full Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={personName}
                onChange={(e) => setPersonName(e.target.value)}
                placeholder="e.g. John Smith"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              />
            </div>

            {/* Drop zone */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Face Images <span className="text-red-500">*</span>
              </label>
              <div
                ref={dropZoneRef}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center cursor-pointer hover:border-violet-400 hover:bg-violet-50 transition-colors"
              >
                <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-medium text-slate-600">
                  Drop images here or click to browse
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  JPG, PNG, WebP — multiple images improve accuracy
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  className="hidden"
                  onChange={(e) => e.target.files && handleFiles(e.target.files)}
                />
              </div>
            </div>

            {/* Image previews */}
            {imagePreviews.length > 0 && (
              <div>
                <p className="text-xs font-medium text-slate-500 mb-2">
                  Selected Images ({imagePreviews.length})
                </p>
                <div className="grid grid-cols-4 sm:grid-cols-6 gap-3">
                  {imagePreviews.map((prev, idx) => (
                    <div
                      key={idx}
                      className="relative group rounded-lg overflow-hidden border border-slate-200 aspect-square"
                    >
                      <img
                        src={prev.url}
                        alt={`Preview ${idx + 1}`}
                        className="w-full h-full object-cover"
                      />
                      {/* Status overlay */}
                      {prev.status === 'ok' && (
                        <div className="absolute inset-0 bg-emerald-500/30 flex items-center justify-center">
                          <CheckCircle className="w-5 h-5 text-emerald-600" />
                        </div>
                      )}
                      {prev.status === 'error' && (
                        <div className="absolute inset-0 bg-red-500/30 flex items-center justify-center" title={prev.message}>
                          <XCircle className="w-5 h-5 text-red-600" />
                        </div>
                      )}
                      {/* Remove button */}
                      {prev.status === 'pending' && (
                        <button
                          type="button"
                          onClick={() => removePreview(idx)}
                          className="absolute top-1 right-1 w-5 h-5 bg-red-500 rounded-full text-white text-xs hidden group-hover:flex items-center justify-center"
                        >
                          ×
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Messages */}
            {uploadError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-center gap-2">
                <XCircle className="w-4 h-4 flex-shrink-0" />
                {uploadError}
              </div>
            )}
            {uploadSuccess && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 flex-shrink-0" />
                {uploadSuccess}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-1">
              <button
                type="submit"
                disabled={uploading}
                className="flex-1 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {uploading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                    Registering…
                  </>
                ) : (
                  <>
                    <UserPlus className="w-4 h-4" />
                    Register Person
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 border border-slate-300 text-slate-600 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Persons Grid */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <Users className="w-4 h-4 text-slate-400" />
          Registered Persons
        </h2>

        {personsLoading && (
          <div className="text-sm text-slate-400 py-6 text-center">Loading…</div>
        )}

        {!personsLoading && (!persons || persons.length === 0) && (
          <div className="bg-white rounded-xl border border-slate-200 py-12 flex flex-col items-center justify-center text-center shadow-sm">
            <Users className="w-10 h-10 text-slate-300 mb-3" />
            <p className="text-slate-500 font-medium">No persons registered yet</p>
            <p className="text-slate-400 text-sm mt-1">
              Add people to enable face recognition in the live feed.
            </p>
          </div>
        )}

        {persons && persons.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {persons.map((person) => (
              <div
                key={person.id}
                className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden hover:shadow-md transition-shadow"
              >
                {/* Thumbnail */}
                <div className="h-36 bg-gradient-to-br from-violet-50 to-indigo-50 flex items-center justify-center relative">
                  {person.thumbnail_b64 ? (
                    <img
                      src={`data:image/jpeg;base64,${person.thumbnail_b64}`}
                      alt={person.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-16 h-16 rounded-full bg-violet-100 flex items-center justify-center">
                      <Users className="w-8 h-8 text-violet-400" />
                    </div>
                  )}
                  {/* Delete button */}
                  <button
                    onClick={() => handleDelete(person.id)}
                    disabled={deletingId === person.id}
                    className="absolute top-2 right-2 w-8 h-8 rounded-full bg-white/90 hover:bg-red-50 border border-slate-200 hover:border-red-300 flex items-center justify-center text-slate-400 hover:text-red-500 transition-colors shadow-sm disabled:opacity-50"
                    title="Delete person"
                  >
                    {deletingId === person.id ? (
                      <div className="w-3 h-3 border border-red-400 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Trash2 className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>

                {/* Info */}
                <div className="p-4">
                  <p className="font-semibold text-slate-900 truncate">{person.name}</p>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <Camera className="w-3 h-3" />
                      {person.image_count} image{person.image_count !== 1 ? 's' : ''}
                    </span>
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <Brain className="w-3 h-3" />
                      {person.encoding_count} encoding{person.encoding_count !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <div className="mt-2">
                    <span className="inline-flex items-center gap-1 text-xs font-medium bg-violet-50 text-violet-700 px-2 py-0.5 rounded-full border border-violet-100">
                      <CheckCircle className="w-3 h-3" />
                      Registered
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
