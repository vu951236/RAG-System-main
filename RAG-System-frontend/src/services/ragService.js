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

    uploadFile: async (file) => {

        const formData = new FormData();
        formData.append("file", file);

        return axiosClient.post(
            `${RAG_URL}/upload`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );

    },

};

export default ragService;