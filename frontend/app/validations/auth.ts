
import { z } from 'zod';
//Register
export const registerSchema = z
  .object({
    fullName: z
      .string()
      .trim()
      .min(1, 'Full name is required'),

    email: z
      .string()
      .trim()
      .email('Please enter a valid email address'),

    password: z
      .string()
      .min(
        8,
        'Min 8 chars, 1 uppercase, 1 number, 1 special character'
      )
      .regex(
        /[A-Z]/,
        'Min 8 chars, 1 uppercase, 1 number, 1 special character'
      )
      .regex(
        /\d/,
        'Min 8 chars, 1 uppercase, 1 number, 1 special character'
      )
      .regex(
        /[@$!%*?&]/,
        'Min 8 chars, 1 uppercase, 1 number, 1 special character'
      ),

    confirmPassword: z
      .string()
      .min(
        1,
        'Please confirm your password'
      ),

    termsAccepted: z
      .boolean()
      .refine(
        (value) => value === true,
        'You must accept the terms and conditions'
      ),
  })
  .refine(
    (data) =>
      data.password === data.confirmPassword,
    {
      message: 'Passwords do not match',
      path: ['confirmPassword'],
    }
  );

export type RegisterFormData =
  z.infer<typeof registerSchema>;

//Forgot password
export const forgotPasswordSchema =
  z.object({
    email: z
      .string()
      .trim()
      .min(
        1,
        'Email address is required'
      )
      .regex(
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        'Please enter a valid email address'
      ),
  });

export type ForgotPasswordFormData =
  z.infer<typeof forgotPasswordSchema>;
//Reset passwrod
const resetPasswordMessage =
  'Password must contain at least 8 characters, 1 uppercase letter, 1 number, and 1 special character.';

export const resetPasswordSchema =
  z
    .object({
      password: z
        .string()
        .min(
          8,
          resetPasswordMessage
        )
        .regex(
          /[A-Z]/,
          resetPasswordMessage
        )
        .regex(
          /\d/,
          resetPasswordMessage
        )
        .regex(
          /[@$!%*?&]/,
          resetPasswordMessage
        )
        .regex(
          /^[A-Za-z\d@$!%*?&]+$/,
          resetPasswordMessage
        ),

      confirmPassword: z
        .string()
        .min(
          1,
          'Please confirm your password.'
        ),
    })
    .refine(
      (data) =>
        data.password ===
        data.confirmPassword,
      {
        message:
          'Passwords do not match.',
        path: ['confirmPassword'],
      }
    );

export type ResetPasswordFormData =
  z.infer<typeof resetPasswordSchema>;