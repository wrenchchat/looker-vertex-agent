# Updated OpenAPI Specification
```yaml
openapi: 3.0.0
info:
  title: Enhanced Vertex AI Agent System
  version: 2.0.0
  description: Integrated system for Looker, dbt, GCP, and Omni assistance
servers:
  - url: 'https://generativelanguage.googleapis.com/v1beta'
paths:
  /models/{model}:generateContent:
    post:
      summary: Enhanced content generation with multi-agent support
      operationId: generateContent
      parameters:
        - in: path
          name: model
          required: true
          schema:
            type: string
            default: gemini-2.0-pro
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EnhancedGenerateContentRequest'
components:
  schemas:
    EnhancedGenerateContentRequest:
      type: object
      properties:
        contents:
          type: array
          items:
            type: object
            properties:
              parts:
                type: array
                items:
                  type: object
                  properties:
                    text:
                      type: string
                    file:
                      type: object
                      properties:
                        mimeType:
                          type: string
                        data:
                          type: string
        generationConfig:
          type: object
          properties:
            temperature:
              type: number
              default: 0.7
            topK:
              type: integer
              default: 40
            topP:
              type: number
              default: 0.95
            maxOutputTokens:
              type: integer
              default: 2048
        tools:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              parameters:
                type: object
```