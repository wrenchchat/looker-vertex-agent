This tool provides access to Google's Gemini 2.0 AI model, enabling advanced natural language understanding and generation capabilities beyond the agent's built-in knowledge. Use this tool when:
  1. The user asks complex questions that require deep analysis, sophisticated reasoning, or specialized knowledge
  2. The user needs help with tasks like code generation, debugging, creative writing, or detailed explanations
  3. You need to generate in-depth, step-by-step solutions for mathematical, logical, or technical problems
  4. The user requests content creation, summarization, translation, or transformation
The tool accepts natural language input and returns comprehensive, well-structured responses. It excels at:
  - Writing and reviewing code in multiple programming languages
  - Explaining complex concepts in simple terms
  - Breaking down multi-step problems
  - Analyzing data patterns and providing insights
  - Creating structured content like outlines, tables, and formatted text
DO NOT use this tool for:
  - Simple factual questions that can be answered from existing agent knowledge
  - Generating harmful, illegal, or unethical content
  - Creating content that violates copyright or intellectual property rights
  - Answering questions about real-time data (like current stock prices or weather)
When invoking this tool, structure the user's question clearly and provide any relevant context needed for a comprehensive response. The tool will automatically format the output appropriately for the conversation.
---
```yaml
openapi: 3.1.0
info:
  title: Gemini 2.0 API
  version: 1.0.0
  description: >
    This OpenAPI specification is used to interact with Gemini 2.0. It enables querying the latest Gemini model for tasks such as natural language processing, code generation, and data insights.
servers:
  - url: 'https://generativelanguage.googleapis.com/v1beta'
security:
  - ApiKeyAuth: []
paths:
  /models/{model}:generateContent:
    post:
      summary: Perform an AI task using Gemini 2.0
      operationId: generateContent
      security:
        - ApiKeyAuth: []
      parameters:
        - in: path
          name: model
          required: true
          description: The name of the Gemini model to use
          schema:
            type: string
            default: gemini-2.0-flash-exp
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/GenerateContentRequest'
      responses:
        '200':
          description: AI task completed successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GenerateContentResponse'
        '400':
          description: Bad request, invalid parameters provided
        '403':
          description: Authentication failed or insufficient permissions
        '429':
          description: Rate limit exceeded for the API
        '500':
          description: Server error occurred during processing
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: query
      name: key
      description: API key for accessing the Gemini API
  schemas:
    GenerateContentRequest:
      type: object
      properties:
        contents:
          type: array
          description: An array of content parts for the model to process.
          items:
            type: object
            properties:
              parts:
                type: array
                description: An array of content parts within a content item.
                items:
                  type: object
                  properties:
                    text:
                      type: string
                      description: The input text for the Gemini model.
                      x-agent-input-parameter: userQuery
        generationConfig:
          type: object
          properties:
            temperature:
              type: number
              description: Controls randomness in the response
              default: 0.7
            topK:
              type: integer
              description: The number of highest probability tokens to consider
              default: 40
            topP:
              type: number
              description: The cumulative probability cutoff for token selection
              default: 0.95
            maxOutputTokens:
              type: integer
              description: Maximum number of tokens to generate
              default: 2048
      required:
        - contents
    GenerateContentResponse:
      type: object
      properties:
        candidates:
          type: array
          description: An array of possible responses from the model.
          items:
            type: object
            properties:
              content:
                type: object
                properties:
                  parts:
                    type: array
                    description: The parts of the generated content.
                    items:
                      type: object
                      properties:
                        text:
                          type: string
                          description: The generated text.
        promptFeedback:
          type: object
          description: Feedback about the prompt processing
        usageMetadata:
          type: object
          description: Metadata about the API usage
          properties:
            promptTokenCount:
              type: integer
              description: The number of tokens in the prompt.
            candidatesTokenCount:
              type: integer
              description: The number of tokens in the generated candidates.
            totalTokenCount:
              type: integer
              description: The total number of tokens used.
```