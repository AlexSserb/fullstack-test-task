"use client";

import {useState} from "react";
import {Alert, Col, Container, Row} from "react-bootstrap";
import {AlertsTable} from "@/components/AlertsTable";
import {FilesTable} from "@/components/FilesTable";
import {FileUploadModal} from "@/components/FileUploadModal";
import {PageHeader} from "@/components/PageHeader";
import {useData} from "@/hooks/useData";
import {useFileUpload} from "@/hooks/useFileUpload";

export default function Page() {
  const {files, alerts, isLoading, errorMessage, setErrorMessage, loadData} = useData();
  const [showModal, setShowModal] = useState(false);

  const {title, setTitle, setSelectedFile, isSubmitting, handleSubmit} =
    useFileUpload({
      onSuccess: async () => {
        setShowModal(false);
        await loadData();
      },
      onError: setErrorMessage,
    });

  return (
    <Container fluid className="py-4 px-4 bg-light min-vh-100">
      <Row className="justify-content-center">
        <Col xxl={10} xl={11}>
          <PageHeader onRefresh={() => void loadData()} onAddFile={() => setShowModal(true)}/>
          {errorMessage ? (
            <Alert variant="danger" className="shadow-sm">
              {errorMessage}
            </Alert>
          ) : null}
          <FilesTable files={files} isLoading={isLoading}/>
          <AlertsTable alerts={alerts} isLoading={isLoading}/>
        </Col>
      </Row>
      <FileUploadModal
        show={showModal}
        onHide={() => setShowModal(false)}
        title={title}
        onTitleChange={setTitle}
        onFileChange={setSelectedFile}
        isSubmitting={isSubmitting}
        onSubmit={handleSubmit}
      />
    </Container>
  );
}