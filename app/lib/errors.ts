export class APIAuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "APIAuthError";
  }
}
