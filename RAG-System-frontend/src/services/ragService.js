import axiosClient from "../api/axiosClient";

const RAG_URL = "/rag";

const ragService = {

    createNewConversation: async () => {
        return axiosClient.post(`${RAG_URL}/conversation/new`);
    },

    getConversations: async () => {
        return axiosClient.get(`${RAG_URL}/conversations`);
    },

    getMessagesByConv: async (convId) => {
        return axiosClient.get(`${RAG_URL}/conversation/${convId}/messages`);
    },

    askQuestion: async (convId, question) => {
        return axiosClient.post(
            `${RAG_URL}/conversation/${convId}/ask`,
            { question }
        );
    },

    uploadFile: async (convId, file) => {

        const formData = new FormData();
        formData.append("file", file);

        return axiosClient.post(
            `${RAG_URL}/conversation/${convId}/upload`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );

    },

    downloadPdf: async (convId, fileName) => {

        const res = await axiosClient.get(
            `/rag/conversation/${convId}/file/${fileName}`,
            {
                responseType: "blob"
            }
        );

        const url = window.URL.createObjectURL(new Blob([res.data]));

        const link = document.createElement("a");
        link.href = url;
        link.download = fileName;

        document.body.appendChild(link);
        link.click();

        link.remove();
    },

};

export default ragService;