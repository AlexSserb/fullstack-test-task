import type {FormEvent} from "react";
import {useState} from "react";
import {uploadFile} from "@/api/filesApi";

interface UseFileUploadOptions {
  onSuccess: () => Promise<void>;
  onError: (message: string) => void;
}

export function useFileUpload({onSuccess, onError}: UseFileUploadOptions) {
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim() || !selectedFile) {
      onError("Укажите название и выберите файл");
      return;
    }

    setIsSubmitting(true);
    try {
      await uploadFile(title.trim(), selectedFile);
      setTitle("");
      setSelectedFile(null);
      await onSuccess();
    } catch (error) {
      onError(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsSubmitting(false);
    }
  }

  return {title, setTitle, selectedFile, setSelectedFile, isSubmitting, handleSubmit};
}